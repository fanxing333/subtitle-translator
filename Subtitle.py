from tqdm import tqdm
import time
from translate import translate_by_sentence, translate


class Subtitle:
    def __init__(self, file_path, source):
        self.file_path = file_path  # 文件路径
        self.source = source
        self.st_list = []  # 每一段字幕作为一个 dict 存在 list 里面
        self.sentence_list = []

        # read srt file
        with open(file_path, "r") as f:
            self.file_data = f.read()

        # 暂时无用
        self.plain_text = ""

    # transform file data to subtitle list
    def trans_to_list(self):
        sub_dict_list = []
        sub_dict = {}
        for i, line in enumerate(self.file_data.split("\n")):
            if line.isdigit():  # 字幕编号
                sub_dict['number'] = int(line)
                sub_dict['en_srt'] = ""

            elif ' --> ' in line:  # 时间戳
                start, end = line.split(' --> ')
                sub_dict['start_time'] = start
                sub_dict['end_time'] = end

            elif line.strip():  # 字幕内容
                sub_dict['en_srt'] += line + " "

            else:  # 字幕结束，将字幕字典存储到列表中
                if sub_dict.get("number") is not None:
                    sub_dict['en_srt'] = sub_dict['en_srt'][:-1]
                    sub_dict_list.append(sub_dict)
                sub_dict = {}

        # 如果字幕文件来源是 youtube 那就按照它的格式解析
        if self.source == "youtube":
            sub_dict_modified = {
                "number": None,
                "start_time": None,
                "end_time": None,
                "en_srt": "",
                "cn_srt": ""
            }

            sub_dict_modified_list = []
            number = 1
            for sub_dict in sub_dict_list:
                # 如果是一句话中的第一段
                if sub_dict_modified["number"] is None:
                    sub_dict_modified["number"] = number
                    number += 1
                    sub_dict_modified["start_time"] = sub_dict["start_time"]

                # 每句话都添加进字典里
                sub_dict_modified["en_srt"] += sub_dict["en_srt"] + " "

                # 如果一句话结束了
                if sub_dict["en_srt"][-1] == ("." or "?" or "!"):
                    sub_dict_modified["end_time"] = sub_dict["end_time"]
                    sub_dict_modified_list.append(sub_dict_modified)
                    sub_dict_modified = {
                        "number": None,
                        "start_time": None,
                        "end_time": None,
                        "en_srt": "",
                        "cn_srt": ""
                    }

            return sub_dict_modified_list

        return sub_dict_list

    # 导出单/双语言字幕文件
    def export_srt(self, target_path):
        with open(target_path, 'w') as file:
            for sub in self.st_list:
                file.write(str(sub['number']) + '\n')
                file.write(sub['start_time'] + ' --> ' + sub['end_time'] + '\n')
                file.write(sub['en_srt'] + '\n')
                if sub['cn_srt'] != "":
                    file.write(sub['cn_srt'] + '\n')
                file.write('\n')

        print("export to srt file successfully!")

    # 暂时无用
    def get_excerpt(self):
        for sub in self.st_list:
            self.plain_text += sub["en_srt"]

    def get_segment_list(self):
        # 把每一段都存储到一个列表，段的划分受限于 tokens 的大小，段落越长，机器的上下文理解力就越好，但越容易超出限制。
        segment_list = []
        text = ""
        for st in self.st_list:
            text += st["en_srt"] + "#"
            if len(text) > 2000:
                segment_list.append(text[:-1])
                text = ""
        segment_list.append(text[:-1])

        # 把 segment 分批翻译，并按句子划分存到 sentence_list
        for i in tqdm(range(len(segment_list)), desc="Processing", ncols=80, leave=True):
            while True:
                try:
                    res = translate(segment_list[i])
                    break
                except Exception as e:
                    print(e)

            sub_sentence = res.split("#")
            if len(segment_list[i].split("#")) == len(sub_sentence):  # 完美结果
                self.sentence_list += sub_sentence
                print("完美分割")
            elif len(segment_list[i].split("#")) > len(sub_sentence):  # 有些句子没有分开
                start_num = len(self.sentence_list) + 1
                self.sentence_list += sub_sentence
                end_num = len(self.sentence_list) + 1
                unaligned_num = end_num - start_num - len(sub_sentence)

                print(f"第 {start_num} - {end_num} 号的句子没有分开，有 {unaligned_num} 行unaligned")
            else:  # 奇怪的错误
                print("奇怪的错误")

    def translate(self):
        for i, sub in enumerate(self.st_list):
            if i < len(self.sentence_list):
                sub["cn_srt"] = self.sentence_list[i]
            else:
                break
            #sub["cn_srt"] = translate_by_sentence(sub["en_srt"])


if __name__ == "__main__":
    # 1. 初始化 读取 srt 文件
    subtitle = Subtitle(file_path="test_case/Lecture 1 - Introduction and Logistics.en.srt", source="youtube")
    # 2. 根据不同的字幕风格转导为相应的字幕格式
    subtitle.st_list = subtitle.trans_to_list()

    subtitle.get_segment_list()
    # 3. 翻译
    subtitle.translate()

    # 导出为双语字幕文件
    subtitle.export_srt("test_case/l1_export.srt")
