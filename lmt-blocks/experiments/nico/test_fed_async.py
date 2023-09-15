'''
Created by Nicolas Torquet at 19/04/2023
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''

from blocks.FED3.Fed3Manager3 import Fed3Manager3

import Trial_DNMTP

# def deviceListener(event):
#     '''
#     Listen the gate:
#      - an animal entered the test zone -> get its RFID number -> start a session
#      - an animal exit the test zone - end a session
#     '''
#
#     if "nose poke" in event.description:
#         if "right" in event.data:
#             print('right')
#             fed.click()
#         if "left" in event.data:
#             print('left')
#             fed.light()



if __name__ == '__main__':
    fed = Fed3Manager3(name="fed", comPort="COM91")
    # fed.addDeviceListener(deviceListener)
    trial = Trial_DNMTP.TrialHabituationLight(fed)



