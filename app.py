from flask import Flask, redirect, request, Response
import requests

app = Flask(__name__)

# قائمة القنوات - استبدلها بقنواتك المجانية
CHANNELS = {
    "318197": "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ae/sharjah_sports.m3u8",
    "358222": "https://stream.example.com/channel2.m3u8",
    "433740": "https://stream.example.com/channel3.m3u8",
    "1001": "https://stream.example.com/channel4.m3u8",
    "1002": "https://stream.example.com/channel5.m3u8",
}
