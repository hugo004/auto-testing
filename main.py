from selenium import webdriver
from os import path
from enum import Enum

import time
import sys
import json
import rstr

"""
format:{
    "name": [string],
    "target": [string],
    "quit": [bool]
    steps:[
        {
            "name": [string],
            "xpath": [string],
            "type": [string],
            "action": [string],
            "value": [string],
            "delay": [int],
            "rule": [regex],
            "generate": [bool]
        }
    ]
}
"""

class Actions(Enum):
    CLICK = 'click'
    INPUT = 'input'


def data_generator(rule):
    # rule: regex
    # generate input field data based on rule
    return rstr.xeger(rule)

def main():
    # check file
    file_path = sys.argv[1]
    if not path.exists(file_path):
        print('cannot read file from path')
        exit()

    # read file
    with open(file_path, 'r') as file:
        data = file.read()
    # parse file
    obj = json.loads(data)

    # launch browser
    target_url = obj['target']
    browser = webdriver.Chrome()
    browser.get(target_url)

    current_idx = -1
    quit_on_finish = obj['quit']

    try:
        # loop step
        for idx, step in enumerate(obj['steps']):
            current_idx = idx
            # use xpath attribute as first priority if had
            if step['xpath']:
                el = browser.find_element_by_xpath(step['xpath'])
            else:
                # query element based on name attribute
                el_name = step['name']
                if not el_name:
                    print('cannot query empty element name')
                    exit()
                el = browser.find_element_by_name(step)

            if not el:
                print('cannot find element')
                exit()

            # total two action for now (e.g. click / input)
            time.sleep(step['delay'])
            action = step['action']
            if Actions(action) == Actions.CLICK:
                el.click()
            elif Actions(action) == Actions.INPUT:
                auto_generate = False
                if 'generate' in step:
                    if step['generate']:
                        if 'rule' in step:
                            el.send_keys(data_generator(step['rule']))
                            auto_generate = True

                if not auto_generate:
                    el.send_keys(step['value'])
            else:
                print(f'action {action} not support')
                exit()
    except Exception as e:
        print(f'fail on step {current_idx + 1}\n')
        print(e)
    finally:
        if quit_on_finish:
            time.sleep(3)
            browser.quit()



if __name__ == '__main__':
    main()