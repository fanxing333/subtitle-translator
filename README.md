# subtitle-translator
基于 **gpt-3.5-turbo** 将 YouTube 自动生成的英文字幕、Whisper 自动识别的英文字幕或其它标准 srt 字幕文件转换为中文字幕或中英双语字幕的脚本。传统的流式音频识别会有一些突兀的事实错误，且中文实时翻译的效果更差。希望 gpt 可以通过学习上下文来避免此类错误。

### 功能说明
根据提供的字幕文件的结构选择合适的翻译策略，输出中英双语字幕或中文字幕。理论上来讲字幕文件格式越规范，GPT 的翻译效果就越好。\
目前有逐句翻译和逐段翻译两种策略。它们是成本和效率之间的权衡。
1. 逐句翻译和普通的翻译机器没有什么区别，但是翻译质量依赖于英文字幕的质量。比如有时候英文字幕比较杂乱，句子之间没有明确的分隔，这样得到的翻译质量也不会太好，第二个缺点是句子太短，请求太快会触发 openAI 的请求上限（虽然官网标的普通用户是 20RPM，但我每隔 5秒 请求一次也会触发警告，很迷！~~刚刚绑了信用卡，等我再试试付费用户的速率~~真的很快，再也没有 Rate Limited 了！）；

2. 逐段翻译可以保留上下文的信息，但是 AI 不太听话，小概率会在翻译的过程中删除句子之间的分隔符，导致我不能还原到对应的句子。第二个缺点是上下文信息太多会让 AI 把表达相近的两个句子翻译成一句话，因为英文本身就比较啰嗦，有时候会表达重复的意思。所以这里又写了一个脚本，可以在人工的基础上快速的让中文 align（其实目前没有什么好的办法更加智能，寄！）。

### 使用教程
#### 获取英文字幕文件
1. 使用 [you-get](https://github.com/soimort/you-get) 下载视频，字幕会和视频一起被下载
    ```bash
    # 查看可以下载的信息，可以选择分辨率和文件等
    you-get -i 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
    # 选择一个 itag 下载
    you-get -itag=123 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
    ```
2. 或者使用 [Whisper](https://github.com/openai/whisper) 识别本地音视频文件并输出字幕文件
    ```bash
    whisper YOUR_{VIDEO/AUDIO}_FILE --model {medium/large} --output_format srt
    ```
#### 设置 openAI 的 API
```bash
export OPENAI_API="sk_YOUR_SECRET_KEY"
```
#### 执行脚本进行翻译，输出双语字幕文件
```bash
python main.py --source_file=YOUR_SRT_FILE_PATH --target_file=OUTPUT_SRT_FILE_PATH
```
#### 运行效果
1. 在 Terminal 中执行
![execute in terminal](static/running_screenshot1.png)
   
2. 输出的日志文件
![logger file](static/running_screenshot2.png)
   
GPT 感觉还是不太稳定，有时候会出现一些意想不到的错误。比如这一次的回答里出现了无关信息。感觉它的错误率在 0.1-1% 之间。
![AI error](static/running_error1.png)
#### 对生成的字幕文件做校正
如果使用逐段翻译策略，很有可能最后生成的中文字幕没有对齐。打开输出的字幕文件在需要隔断的地方加“#”键，运行 align_script.py 脚本实现自动隔断。

### 结语
经过本人这几天的使用体验，我认为机器翻译仍然无法与专业的字幕组翻译相媲美，但对于日常观看的视频而言，GPT 的水平已经足够使用了。
希望这个工具能够帮助那些对其他世界感到好奇但因语言障碍而无法探索的朋友们。
也希望这个工具只是人生中的一个过渡，通过它尽早实现外语自由。