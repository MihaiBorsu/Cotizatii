#!/bin/bash

# sudo systemctl status cotizatii.service
# sudo systemctl start cotizatii.service
# sudo systemctl stop cotizatii.service
# sudo systemctl enable cotizatii.service

/home/borsu/.local/bin/webhookd -scripts /home/borsu/Documents/cotizatii/Cotizatii/scripts -listen-addr :8089 >> /home/borsu/Documents/cotizatii/Cotizatii/server_logs.txt
