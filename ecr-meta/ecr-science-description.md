## MRR-2 plugin

Plugin for transfer and processing of MRR-2 data. This version uses the RaProM package to process the MRR-2 data. RaProM is available at: https://github.com/AlbertGBena/RaProM/tree/master. 

# Science

The Micro Rain Radar 2 is a vertically pointing Ka-band radar that detects precipitation in a vertical column above the MRR 2. This allows us to examine the vertical structure of precipitation in the column and estimate hourly rainfall rates in the column. In addition, the Mrr 2 records the particle fall speeds in the column, allowing for the ability to distinguish between snow, rain, and graupel.

# Usage

Log into a waggle node:

Clone this repository on the Waggle node:
```
git clone https://github.com/rcjackson/plugin-mrr2.git
cd plugin-mrrpro
```

The MRR-2 plugin is built and run using the following command on the Waggle node:
```
sudo pluginctl run --debug --name mrrpro --selector zone=core $(sudo pluginctl build .)
```

The MRR-2 plugin needs to run continuously to transfer the data from the MRR-2 via serial. It processes the retrieved data at hourly intervals at the top of every hour.

# Data Query
To query the last hour of data, do:
```
df = sage_data_client.query(
            start="-1h",
            filter={"name": "upload", "vsn": "W08D",
                    "task": "mrr2"},).set_index("timestamp")
```                   
The names of the available files are in the *value* key of the dataframe. Both hourly .raw files and processed .nc files are uploaded to beehive so that the user can either use the processed data or apply their own processing to the raw data (i.e. with other MRR packages like ImProToo).

# References
Garcia-Benadi A, Bech J, Gonzalez S, Udina M, Codina B, Georgis J-F. Precipitation Type Classification of Micro Rain Radar Data Using an Improved Doppler Spectral Processing Methodology. Remote Sens. 2020, 12, 4113.DOI: 10.3390/rs12244113

