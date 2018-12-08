#!/bin/bash
# 生成字体下载链接
awk -F'[()]+' '{print $6}' google.css |sort|uniq > links.txt
echo 'http://baidu.com' >> links.txt
dos2unix links.txt
echo "downloading the files"
for link in $(cat links.txt):
    do
        echo "${link}"
        name=$(echo "${link}"|awk -F'/' '{print $NF}')
        echo "${name}"
        curl "${link}" --output "${name}"
    done