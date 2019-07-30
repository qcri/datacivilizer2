# Data Civilizer 2.0

### Clone the DC2 repository
```
# clone using https
git clone --recursive https://github.com/elkindi/dc2.git
```
    

### Install the dependencies

1. Node.js dependencies
```
npm install express
npm install topological-sort
```

2. Python dependencies
```
hdf5storage (using pip: pip install hdf5storage)
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
