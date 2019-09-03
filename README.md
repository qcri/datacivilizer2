# Data Civilizer 2.0

### Clone the DC2 repository
```
# clone using https
git clone --recursive https://github.com/qcri/datacivilizer2.git
```

### Run the Node.js server on Docker

1. Build the image
```
cd server/
docker build -t dc2 .
```

2. Start a container from the image
```
docker run -p 8080:8080 -d dc2
```

3. Start a container from the image with the segment data folder attached
```
docker run -p 8080:8080 <path_to_segment_data_folder>:/usr/src/app/Data/second_dataset_from_cpd_eeg_10s_split -d dc2
```

4. Stop the container
```
docker stop <containerID>
```

### Or

### Install the dependencies

1. Node.js dependencies
```
npm install express
npm install topological-sort
npm install csv-parser
npm install path-sort
npm install chart.js
npm install request
```

2. Python dependencies
```
pip install matplotlib
pip install tensorboardX
pip install torch
pip install hdf5storage
pip install tqdm
pip install requests
```

3. You need to have a working version of Matlab (tested with R2019a and R2018).

4. You need the MATLAB Engine API for Python: [Get Started with MATLAB Engine API for Python](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html?s_tid=CRUX_lftnav)

5. You need all the Matlab packages emploied in the MATLAB scripts.
	- an easy way to check if all the packages are installed is to run the scripts from Matlab first (with small test data), there it will be possible to install missing ones.

### Run the Node.js server:
```
cd server/
node server.js
```

### Test DC2
```
Open the following URL on your browser: localhost:8080
```
