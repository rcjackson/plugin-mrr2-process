## MRR-PRO plugin

Plugin for transfer and processing of MRR-PRO data. This current version only supports the transfer
of raw data. Future versions will include processing the raw data to remove artifacts and dealias
Doppler spectra.

# Science

The Micro Rain Radar (MRR) Pro is a vertically pointing Ka-band radar that detects precipitation in a vertical column above the MRR Pro. This allows us to examine the vertical structure of precipitation in the column and estimate hourly rainfall rates in the column. In addition, the MRR Pro records the particle fall speeds in the column, allowing for the ability to distinguish between snow, rain, and graupel.

# Usage

Log into a waggle node:

Clone this repository on the Waggle node:
```
git clone https://github.com/rcjackson/plugin-mrrpro.git
cd plugin-mrrpro
```

The MRR-PRO plugin is built and runusing the following command on the Waggle node:
```
sudo pluginctl run --debug --name mrrpro --selector zone=core $(sudo pluginctl build .)
```

The MRR-PRO plugin takes in one parameter, the number of files to download. The default value is 1, which will only transfer the latest file. To adjust this, simply edit the Dockerfile's last line. For example, to transfer all files to Beehive:
```
ENTRYPOINT ["python3", "main.py", "-n 0"]
```

To transfer the latest 24 hours:
For example, to transfer all files to Beehive:
```
ENTRYPOINT ["python3", "main.py", "-n 24"]
```

# Data Query
To query the last hour of data, do:
```
df = sage_data_client.query(
            start="-1h",
            filter={"name": "upload", "vsn": "W08D",
                   "plugin": "10.31.81.1:5000/local/plugin-mrrpro"},).set_index("timestamp")
```                   
The names of the available files are in the *value* key of the dataframe.
