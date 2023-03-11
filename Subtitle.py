from tqdm import tqdm
import time

from logger import logger
from translate import translate_by_sentence, translate

def sub_dict_init():
    return {"number": None, "start_time": None, "end_time": None, "en_srt": "", "cn_srt": ""}

class Subtitle:
    def __init__(self, file_path, style):
        self.file_path = file_path  # 文件路径
        self.style = style  # 字幕文件风格
        self.st_list = []  # 每一段字幕文本作为一个 dict 存在 list 里面
        self.sentence_list = []
        self.segment_list = []

        # read srt file
        with open(file_path, "r") as f:
            self.file_data = f.read()

    # transform file data to subtitle list
    def trans_to_list(self):
        sub_dict_list = []
        sub_dict = sub_dict_init()
        for i, line in enumerate(self.file_data.split("\n")):
            if line.isdigit():  # 字幕编号 number
                sub_dict['number'] = int(line)

            elif ' --> ' in line:  # 时间点 timecode
                start, end = line.split(' --> ')
                sub_dict['start_time'] = start
                sub_dict['end_time'] = end

            elif line.strip():  # 字幕文本 subtitle text
                # 如果一条字幕文本换行了，则合并为一行
                sub_dict['en_srt'] += line + " "

            else:  # 字幕结束，将字幕字典存储到列表中
                if sub_dict.get("number") is not None:
                    sub_dict['en_srt'] = sub_dict['en_srt'][:-1]
                    sub_dict_list.append(sub_dict)
                sub_dict = sub_dict_init()

        # 如果字幕文件来源是 youtube 那就按照它的格式解析
        if self.style == "youtube":
            sub_dict_modified = sub_dict_init()

            sub_dict_modified_list = []
            number = 1
            for sub_dict in sub_dict_list:
                # 如果是一句话中的第一段
                if sub_dict_modified["number"] is None:
                    sub_dict_modified["number"] = number
                    number += 1
                    sub_dict_modified["start_time"] = sub_dict["start_time"]

                sub_dict_modified["en_srt"] += sub_dict["en_srt"] + " "

                # 不管是人工制作还是机器识别的字幕，主要的目的还是将文本显示在视频上方
                # 所以不会遵循某种格式来制作字幕，也没有这种标准，这给字幕文件的自动化转化造成了很大的麻烦
                # 如何来界定一句话——为了尽量避免让 GPT 翻译没有上下文的半句话，造成翻译失真
                # 根据字幕文件结尾是否是 {",", ".", "?"} 判断一句话是否结束
                if sub_dict["en_srt"][-1] == ("." or "?" or "!"):
                    sub_dict_modified["end_time"] = sub_dict["end_time"]
                    sub_dict_modified_list.append(sub_dict_modified)
                    sub_dict_modified = sub_dict_init()
                    continue

                # 由于有些字幕根本就没有标点符号，所以这里根据长度将其分割，还有什么好办法？
                if len(sub_dict_modified["en_srt"]) > 300:
                    sub_dict_modified["end_time"] = sub_dict["end_time"]
                    sub_dict_modified_list.append(sub_dict_modified)
                    sub_dict_modified = sub_dict_init()
                    continue

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

        logger.info("export to srt file successfully!")

    def get_segment_list(self):
        # 把每一段都存储到一个列表，段的划分受限于 tokens 的大小，段落越长，机器的上下文理解力就越好，但越容易超出限制。
        text = ""
        seg_start = 1
        for i, st in enumerate(self.st_list):
            text += st["en_srt"] + "#"
            if len(text) > 1500:
                self.segment_list.append({
                                        "start": seg_start,
                                        "end": i+1,
                                        "length": i+1-seg_start,
                                        "text": text[:-1]
                                    })
                seg_start = i+2
                text = ""
        # 将最后一个不足长度的 segment 添加到 segment_list
        self.segment_list.append({
                                "start": seg_start,
                                "end": len(self.st_list)+1,
                                "length": len(self.st_list)+1-seg_start,
                                "text": text[:-1]
                            })

    def translate(self, policy):
        if policy == 0:
            # 逐句翻译
            for i in tqdm(range(len(self.st_list)), desc="Processing", ncols=80, leave=True):
                self.st_list[i]["cn_srt"] = translate_by_sentence(self.st_list[i]["en_srt"])

        elif policy == 1:
            # 逐段翻译
            self.get_segment_list()
            # 把 segment 分批翻译，并按句子划分存到 sentence_list
            for i in tqdm(range(len(self.segment_list)), desc="Processing", ncols=80, leave=True):
                seg = self.segment_list[i]
                res = translate(seg["text"])

                sentence_list = res.split("#")
                if seg["length"] == len(sentence_list):  # 完美结果
                    self.sentence_list += sentence_list
                    logger.info("完美分割")

                elif seg["length"] > len(sentence_list):  # 有些句子没有分开
                    self.sentence_list += sentence_list
                    logger.warning(
                        f"第 {seg['start']} - {seg['end']} 号的句子没有分开，有 {seg['length'] - len(sentence_list)} 行unaligned")

                else:  # 奇怪的错误
                    logger.error("奇怪的错误")

            for i, sub in enumerate(self.st_list):
                if i < len(self.sentence_list):
                    sub["cn_srt"] = self.sentence_list[i]
                else:
                    break

if __name__ == "__main__":
    # 1. 初始化 读取 srt 文件
    subtitle = Subtitle(file_path="test_case/Lecture 1 - Introduction and Logistics.en.srt", style="youtube")
    # 2. 根据不同的字幕风格转导为相应的字幕格式
    subtitle.st_list = subtitle.trans_to_list()
    # 3. 翻译
    #subtitle.translate(policy=0)
    # 导出为双语字幕文件
    #subtitle.export_srt("test_case/l1_export.srt")
