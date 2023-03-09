with open("test_case/output.srt", "r") as f:
    file_data = f.read()

sub_dict_list = []
sub_dict = {
    "number": None,
    "start_time": None,
    "end_time": None,
    "en_srt": "",
    "cn_srt": ""
}
for i, line in enumerate(file_data.split("\n")):
    if line.isdigit():  # 字幕编号
        sub_dict['number'] = int(line)

    elif ' --> ' in line:  # 时间戳
        start, end = line.split(' --> ')
        sub_dict['start_time'] = start
        sub_dict['end_time'] = end

    elif "." in line.strip():  # 英文字幕内容
        sub_dict['en_srt'] = line.strip()

    elif "。" in line.strip():  # 中文字幕内容
        sub_dict["cn_srt"] = line.strip()

    else:  # 字幕结束，将字幕字典存储到列表中
        if sub_dict.get("number") is not None:
            sub_dict_list.append(sub_dict)
        sub_dict = {
            "number": None,
            "start_time": None,
            "end_time": None,
            "en_srt": "",
            "cn_srt": ""
        }

for i in range(len(sub_dict_list)):
    #print(i)
    if "#" in sub_dict_list[i]["cn_srt"]:

        split_item = sub_dict_list[i]["cn_srt"].split("#")
        for j in range(len(sub_dict_list)-1, i, -1):
            sub_dict_list[j]["cn_srt"] = sub_dict_list[j-1]["cn_srt"]
        sub_dict_list[i]["cn_srt"] = split_item[0]
        sub_dict_list[i+1]["cn_srt"] = split_item[1]

with open("test_case/output.srt", 'w') as file:
    for sub in sub_dict_list:
        file.write(str(sub['number']) + '\n')
        file.write(sub['start_time'] + ' --> ' + sub['end_time'] + '\n')
        file.write(sub['en_srt'] + '\n')
        if sub['cn_srt'] != "":
            file.write(sub['cn_srt'] + '\n')
        file.write('\n')
