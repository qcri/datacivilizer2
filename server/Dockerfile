FROM node:10

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

# install nodejs dependencies
RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# install python modules
RUN apt-get update
RUN apt-get install -y python3-pip

RUN pip3 install matplotlib
RUN pip3 install tensorboardX
RUN pip3 install torch
RUN pip3 install hdf5storage
RUN pip3 install tqdm
RUN pip3 install requests

# Bundle app source
COPY . .

EXPOSE 8080
CMD [ "node", "server.js" ]