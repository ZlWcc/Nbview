#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 21:31
# @Author  : 21w
# @File    : research.py.py

class mk_wav(object):
    
    def mk_head(self, datasize, voicesize):
        RIFF = b'RIFF'
        info = b'WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data'
        head = RIFF + datasize + info + voicesize
        return head
    
    def source_wav(self,*args):
        block_lenth = 0
        datas = b''.join(args)
        datas_lenth = len(datas) + 44
        if datas_lenth % 1024:
            block_lenth = 1024 - datas_lenth % 1024
        data_size = (datas_lenth + block_lenth - 44).to_bytes(4, 'little')
        voice_size = (datas_lenth + block_lenth - 8).to_bytes(4, 'little')
        head = self.mk_head(data_size, voice_size)
        bytes_stream = head + datas + b'\x00'*block_lenth
        return bytes_stream

    def get_wav(self, wav_bytes, file='default.wav'):
        reste = len(wav_bytes) % 1024
        if reste == 0:
            with open(file, 'ab') as f:
                f.write(wav_bytes)

    def clean_wav(self, file):
        with open(file, 'rb') as f:
            return f.read()[44:]


wav = mk_wav()
file1 = wav.clean_wav(r'source01.wav')
file2 = wav.clean_wav(r'source02.wav')
wav_data = wav.source_wav(*[file1, file2])
wav.get_wav(wav_data, 'des1.wav')


