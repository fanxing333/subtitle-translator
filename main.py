import argparse
from Subtitle import Subtitle

def run(source_file, target_file, translate_policy):
    # 导入字幕文件
    sub_source = Subtitle(file_path=source_file, source="youtube")
    # 转换字幕文件风格
    sub_source.st_list = sub_source.trans_to_list()
    # 字幕文件翻译
    sub_source.translate(policy=translate_policy)
    # 导出为双语字幕文件
    sub_source.export_srt(target_file)

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_file', type=str, help='srt file path')
    parser.add_argument('--target_file', type=str, default="output.srt", help='srt file export path')
    parser.add_argument('--translate_policy', type=int, default=0, help='srt file export path')
    opt = parser.parse_args()
    return opt

def main(opt):
    run(**vars(opt))

if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
