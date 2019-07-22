function saveModelVersions() {
    modelVersions = {'maxSize' : maxSize, 'maxModelId' : maxModelId, 'runCounter' : runCounter, 'hashTable' : hashTable};
    obj = JSON.stringify(modelVersions);

    $.ajax({
        url: '/saveModelVersions',
        type: 'post',
        processData: false,
        data: obj,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            console.log("success!");
        }
    });
};

function getModelVersions() {
    $.ajax({
        url: '/getModelVersions',
        type: 'get',
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        data: null,
        success: function (data) {
            hashTable = data.hashTable;
            runCounter = data.runCounter;
            maxSize = data.maxSize;
            maxModelId = data.maxModelId;
        }
    });
};

function getHash(modelString, maxSize) {
    model = JSON.parse(modelString);

    delete model.class;
    delete model.linkFromPortIdProperty;
    delete model.linkToPortIdProperty;
    delete model.modelData;

    nodes = model.nodeDataArray;
    links = model.linkDataArray;

    for (var nodeId in nodes) {
        delete nodes[nodeId].figure;
        delete nodes[nodeId].fill;
        delete nodes[nodeId].loc;
        delete nodes[nodeId].text;
    }

    for (var linkId in links) {
        delete links[linkId].points;
        delete links[linkId].fromPort;
        delete links[linkId].toPort;
    }

    return Math.abs(murmurhash3_32_gc(JSON.stringify(model),1) % maxSize);
};

/**
 * JS Implementation of MurmurHash3 (r136) (as of May 20, 2011)
 * 
 * @author <a href="mailto:gary.court@gmail.com">Gary Court</a>
 * @see http://github.com/garycourt/murmurhash-js
 * @author <a href="mailto:aappleby@gmail.com">Austin Appleby</a>
 * @see http://sites.google.com/site/murmurhash/
 * 
 * @param {string} key ASCII only
 * @param {number} seed Positive integer only
 * @return {number} 32-bit positive integer hash 
 */

function murmurhash3_32_gc(key, seed) {
    var remainder, bytes, h1, h1b, c1, c1b, c2, c2b, k1, i;
    
    remainder = key.length & 3; // key.length % 4
    bytes = key.length - remainder;
    h1 = seed;
    c1 = 0xcc9e2d51;
    c2 = 0x1b873593;
    i = 0;
    
    while (i < bytes) {
        k1 = 
          ((key.charCodeAt(i) & 0xff)) |
          ((key.charCodeAt(++i) & 0xff) << 8) |
          ((key.charCodeAt(++i) & 0xff) << 16) |
          ((key.charCodeAt(++i) & 0xff) << 24);
        ++i;
        
        k1 = ((((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16))) & 0xffffffff;
        k1 = (k1 << 15) | (k1 >>> 17);
        k1 = ((((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16))) & 0xffffffff;

        h1 ^= k1;
        h1 = (h1 << 13) | (h1 >>> 19);
        h1b = ((((h1 & 0xffff) * 5) + ((((h1 >>> 16) * 5) & 0xffff) << 16))) & 0xffffffff;
        h1 = (((h1b & 0xffff) + 0x6b64) + ((((h1b >>> 16) + 0xe654) & 0xffff) << 16));
    }

    k1 = 0;
    
    switch (remainder) {
        case 3: k1 ^= (key.charCodeAt(i + 2) & 0xff) << 16;
        case 2: k1 ^= (key.charCodeAt(i + 1) & 0xff) << 8;
        case 1: k1 ^= (key.charCodeAt(i) & 0xff);
        
        k1 = (((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16)) & 0xffffffff;
        k1 = (k1 << 15) | (k1 >>> 17);
        k1 = (((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16)) & 0xffffffff;
        h1 ^= k1;
    }
    
    h1 ^= key.length;

    h1 ^= h1 >>> 16;
    h1 = (((h1 & 0xffff) * 0x85ebca6b) + ((((h1 >>> 16) * 0x85ebca6b) & 0xffff) << 16)) & 0xffffffff;
    h1 ^= h1 >>> 13;
    h1 = ((((h1 & 0xffff) * 0xc2b2ae35) + ((((h1 >>> 16) * 0xc2b2ae35) & 0xffff) << 16))) & 0xffffffff;
    h1 ^= h1 >>> 16;

    return h1 >>> 0;
};