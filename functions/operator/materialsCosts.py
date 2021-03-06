from database.baseController import BaseController
from message.messageType import TextImage

database = BaseController()
material_images_source = 'resource/images/materials/'


class MaterialCosts:
    def __init__(self, extra):
        self.keywords = []
        self.operator_list = []
        self.skill_list = []
        self.level_list = {
            '精一': 1, '精1': 1, '精英一': 1, '精英1': 1,
            '精二': 2, '精2': 2, '精英二': 2, '精英2': 2,
            '专一': 3, '专1': 3, '专精一': 3, '专精1': 3,
            '专二': 4, '专2': 4, '专精二': 4, '专精2': 4,
            '专三': 5, '专3': 5, '专精三': 5, '专精3': 5
        }
        self.skill_index_list = {
            '一技能': 1, '二技能': 2, '三技能': 3,
            '1技能': 1, '2技能': 2, '3技能': 3
        }
        keywords = [] + extra

        for key in self.level_list:
            keywords.append('%s 100 n' % key)
            self.keywords.append(key)
        for key in self.skill_index_list:
            keywords.append('%s 100 n' % key)
            self.keywords.append(key)

        operators = database.operator.get_all_operator()
        for item in operators:
            name = item['operator_name']
            keywords.append('%s 100 n' % name)
            self.operator_list.append(name)
            self.keywords.append(name)

        skills = database.operator.get_all_operator_skill()
        for item in skills:
            name = item['skill_name']
            self.skill_list.append(name)
            self.keywords.append(name)

        with open('resource/operators.txt', mode='w', encoding='utf-8') as file:
            file.write('\n'.join(keywords))

    @staticmethod
    def check_evolve_costs(name, level):
        evolve = {1: '一', 2: '二'}

        result = database.operator.find_operator_evolve_costs(name, level)

        text = ''
        if len(result):
            text += '博士，这是干员%s精英%s需要的材料清单\n\n' % (name, evolve[level])
            images = []
            for item in result:
                text += '%s%s X %s\n\n' % (' ' * 12, item['material_name'], item['use_number'])
                images.append(material_images_source + item['material_nickname'] + '.png')

            i = 0
            n = 34
            s = 26
            icons = []
            for index, item in enumerate(images):
                icons.append({
                    'path': item,
                    'size': (35, 35),
                    'pos': (5, s + i)
                })
                i += n

            text = TextImage(text, icons)
        else:
            text += '博士，暂时没有找到相关的档案哦~'

        return text

    @staticmethod
    def check_mastery_costs(name, skill, level, skill_index=0):
        mastery = {1: '一', 2: '二', 3: '三'}

        text = ''
        if skill and skill_index == 0:
            skill_info = database.operator.get_operator_skill_by_name(skill)
            if len(skill_info):
                if name == '' and len(skill_info) > 1:
                    text += '博士，目前存在 %d 个干员拥有【%s】这个技能哦，请用比如「干员一技能专三」这种方式和阿米娅描述吧' % (len(skill_info), skill)
                    return text
                item = skill_info[0]
                skill_index = item['skill_index']
                if name == '':
                    name = item['operator_name']

        result = database.operator.find_operator_skill_mastery_costs(name, level, skill_index)

        if len(result):
            text += '博士，这是干员%s技能专精%s需要的材料清单\n\n' % (name, mastery[level])
            skills = {}
            images = []
            for item in result:
                skill_name = item['skill_name']
                if skill_name not in skills:
                    skills[skill_name] = []
                skills[skill_name].append(item)
            for name in skills:
                text += '%s\n\n' % name
                for item in skills[name]:
                    text += '----%s%s X %s\n\n' % (' ' * 15, item['material_name'], item['use_number'])
                    images.append(material_images_source + item['material_nickname'] + '.png')

            i = 0
            n = 34
            s = 60
            icons = []
            for index, item in enumerate(images):
                if index and index % 3 == 0:
                    i += n
                icons.append({
                    'path': item,
                    'size': (35, 35),
                    'pos': (35, s + i)
                })
                i += n

            text = TextImage(text, icons)
        else:
            text += '博士，暂时没有找到相关的档案哦~'

        return text
