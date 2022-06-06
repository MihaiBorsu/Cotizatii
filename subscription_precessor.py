import gspread
import pprint
import argparse
import re

from oauth2client.service_account import ServiceAccountCredentials

class EasyDict(dict):
    """
    Wrapper over dict so we can get a value as attribute
    Like map.name = "Mike" not just map["name"] = Mike
    Also, missing KEYS are returned as None instead of raising Exception
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

def get_args():
    parser = argparse.ArgumentParser()

    config_group = parser.add_argument_group(title="Config parameters")
    config_group.add_argument("-l", "--log-path", dest="log_path", default=None,
                              help="Path to the ouput log file, if None, stdout is used.")
    config_group.add_argument("-k", "--key-file", dest="key_file", default='./client_key.json',
                              help="Path to the json key file needed to interact with google cloud")
    config_group.add_argument("-f", "--file-name", dest="file_name", default=None,
                              help="Name of the spreadsheat in google drive that we want to interact with")
    config_group.add_argument("--dry-run", dest="dry_run", action="store_true",
                              help="If set to True will not update table")

    data_group = parser.add_argument_group(title="Data group")
    data_group.add_argument("-i", "--id-oncr", dest="id_oncr", default=None,
                              help="This is the unique id for each member")
    data_group.add_argument("-n", "--surname", dest="surname", default=None,
                              help="This is the surname for each member")
    data_group.add_argument("-g", "--given-name", dest="given_name", default=None,
                              help="This is the given name for each member")
    data_group.add_argument("-p", "--pay-for", dest="pay_for", default=[],
                              help="This is the given name for each member", nargs="+")

    functionality_group = parser.add_argument_group(title="Functionality group")
    functionality_group.add_argument("-u", "--update_cotizatie", dest="update_cotizatie", action="store_true",
                              help="If set to True will update the cotizatii table")

    args = parser.parse_args()
    args = vars(args)
    args = EasyDict(args)

    return args

def authorize(key_file):
    scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_file,scope)
    client = gspread.authorize(creds)
    return client

def fetch_sheet(client, file_name):
    sheet = client.open(file_name).sheet1
    print("FETCHED!")
    return sheet

def normalise_id(id):
    id = id.lower()
    id = re.sub(' +', '', id)
    return id

def get_members_ids(sheet):
    python_sheet = sheet.get_all_records()
    return [a_dict["id ONCR"] for a_dict in python_sheet]

def create_new_entry(sheet, id, surname, given_name):
    sheet.insert_row([id, surname, given_name, '', ''], index=2)

def update_entry(sheet, id, pay_for):
    cell_id = sheet.find(id, in_column=1)
    row = cell_id.row

    for pay_period in pay_for:
        cell_pay = sheet.find(pay_period, in_row=1)
        if cell_pay is None: # no pay period in the table case
            print("Payment period cannot be found! This affects the update mechanism, make sure that the form is synced with the table regarding the payment periods values.")
            continue

        column = cell_pay.col

        if sheet.cell(row, column).value == 'TRUE': # double payment for a period case
            cell_notes = sheet.cell(row,4).value
            if cell_notes is None:
                cell_notes = ""
            string = str(cell_notes)+"Double payed for: "+pay_period+"; "
            sheet.update_cell(row,4, string)
        else:
            sheet.update_cell(row, column, '=TRUE')

def handle_entry(sheet, id, surname, given_name, pay_for):

    if id is None:
        print("cannot update with id-oncr field empty")
        return
    else:
        id = normalise_id(id)

    if not pay_for:
        print("cannot update without paying info")
        return

    if id not in get_members_ids(sheet):
        create_new_entry(sheet, id, surname, given_name)
        update_entry(sheet, id, pay_for)
    else:
        update_entry(sheet, id, pay_for)


def main():
    args = get_args()

    if args.dry_run:
        print("Nothing really happens yet") # TbD handle dry run
    else:
        try:
            client = authorize(args.key_file)
            sheet = fetch_sheet(client, args.file_name)
        except:
            print("Connection to google sheet could not be performed, check if the spreadsheet name matches or if the key file is correct")

        if args.update_cotizatie:
                handle_entry(sheet, args.id_oncr, args.surname, args.given_name, args.pay_for)


if __name__ == "__main__":
    main()
