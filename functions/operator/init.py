import json
import jieba

from jieba import posseg
from modules.commonMethods import Reply, word_in_sentence, find_similar_string
from database.baseController import BaseController
from functions.operator.materialsCosts import MaterialCosts

with open('resource/words/voices.json', encoding='utf-8') as voices:
    voices = json.load(voices)['voices']
    keywords = []
    for key in voices:
        keywords.append('%s 100 n' % key)

database = BaseController()
material = MaterialCosts(keywords)
jieba.load_userdict('resource/operators.txt')


class Init:
    def __init__(self):
        self.function_id = 'checkOperator'
        self.keyword = voices + material.keywords

    def action(self, data):

        message = data['text_digits']
        message_ori = data['text']

        words = posseg.lcut(message)
        words_ori = posseg.lcut(message_ori)

        name = ''
        level = 0
        surplus = ''
        voice_key = ''
        skill_index = 0

        for item in words:
            # 获取语音关键词
            if voice_key == '' and item.word in voices:
                voice_key = item.word
                break

        for item in words_ori:
            # 获取干员名
            if name == '' and item.word in material.operator_list:
                name = item.word
                continue
            # 获取专精或精英等级
            if level == 0 and item.word in material.level_list:
                level = material.level_list[item.word]
                continue
            # 获取技能序号
            if skill_index == 0 and item.word in material.skill_index_list:
                skill_index = material.skill_index_list[item.word]
                continue
            surplus += item.word

        skill = find_similar_string(surplus, material.skill_list)

        if name == '' and skill == '':
            return Reply('博士，想查询哪位干员或技能的资料呢？请再说一次吧')

        if level != 0:
            if level <= 2:
                # todo 精英化资料
                result = material.check_evolve_costs(name, level)
            else:
                # todo 专精资料
                level -= 2
                result = material.check_mastery_costs(name, skill, level, skill_index=skill_index)

            return Reply(result)

        if name:
            # todo 语音资料
            if voice_key:
                return self.find_voice(name, voice_key)

            if word_in_sentence(message, ['精英', '专精']):
                return Reply('博士，要告诉阿米娅精英或专精等级哦')

            if word_in_sentence(message, ['语音']):
                return Reply('博士，要告诉阿米娅语音的详细标题哦')

            return Reply('博士，想查询干员%s的什么资料呢' % name)

    @staticmethod
    def find_voice(operator, voice):
        result = database.operator.find_operator_voice(operator, voice)
        if result:
            text = '博士，为您找到干员%s的语音档案：\n\n【%s】\n%s' % (operator, voice, result['voice_text'])
            return Reply(text)
        return Reply('抱歉博士，没有找到干员%s%s相关的语音档案' % (operator, voice))
