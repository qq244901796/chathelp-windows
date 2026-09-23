# ChatHelp 智谱助手 · Windows

基于 [jev-chat/jev-chat-windows](https://github.com/jev-chat/jev-chat-windows) 的**非官方开源修改版**，感谢原作者 rezoch340、Finderchangchang 与所有贡献者。默认直接连接国内智谱 BigModel，以 `glm-4-flash-250414` 完成聊天判断、候选回复和排序。

保留原版界面与本机 RapidOCR。只把回复填入输入框，发送始终手动。当前 Windows 采集适配的是微信；不把安卓的 QQ 支持误认为 Windows 也已实现。

## 下载与使用

1. 从 [本分支 Release](https://github.com/qq244901796/chathelp-windows/releases/tag/v1.0.0-glm) 下载 `chathelp-windows-1.0.0-glm-x64.zip`，完整解压到可写目录。
2. 运行 `chathelp-glm.exe`。Windows 10/11 x64 测试版，未进行 Authenticode 签名；Windows 可能提示未知发布者。校验附件 SHA256，并自行决定是否运行，不建议关闭系统防护。
3. 在 [智谱控制台](https://bigmodel.cn/) 申请自己的 API Key。新安装默认智谱；已有配置可点击“一键应用智谱免费预设”，不会立刻覆盖已存配置。
4. 填一个智谱密钥，判断与起草共用；点击“测试完整流程（虚构对话）”，成功后保存。该测试向所选服务发送虚构文字，检查判断→三条回复→排序。
5. 打开微信聊天窗口、开启采集，核对候选回复后点击填入，再手动发送。暂停或更换会话后旧建议会失效。

截图在本机识别，不需要 OCR Key，不收 OCR API 费用。识别后的聊天文字会发给所选模型。可暂停采集；完全去掉 OCR 后 Windows 版本就不能读取自绘聊天正文。

默认地址 `https://open.bigmodel.cn/api/paas/v4/chat/completions`。免费指指定模型当前推理价格，受并发/配额限制，不保证永久免费。程序不自动切换收费模型；请核对 [官方定价](https://docs.bigmodel.cn/cn/guide/start/pricing)。评分和概率只是模型估计，不能当作对方真实想法。

## 配置与更新

智谱密钥独立存放在当前用户环境变量 `CHATHELP_ZHIPU_API_KEY`（注册表），不会借用 OpenRouter/DeepSeek 的旧密钥。其他设置写在 exe 旁的 `config.json`。转发软件只用 Release 原包，避免夹带自己的配置。

原版供应商仍保留为高级选项，旧配置不会被静默改成智谱。原版自动更新已禁用，请通过本分支 Release 更新。詳见 [隐私](PRIVACY.md)、[变更记录](CHANGELOG.md) 和 [测试范围](TESTING.md)。

## 开源与构建

保留原 MIT LICENSE、NOTICE、Git 历史。由于保留 GPLv3 的 PySide6-Fluent-Widgets，**本组合程序按 GPLv3 分发**，依赖各自许可仍有效；不能只看 MIT 文件就闭源分发。参见 [许可范围](LICENSING.md)、[完整 GPLv3](COPYING)、[第三方清单](THIRD_PARTY_NOTICES.md) 和 `licenses/`。

同一 Release 提供项目源码、依赖对应源码、版本/URL/SHA256 清单和 [构建步骤](BUILDING.md)。不要求维护者的签名密钥即可自行构建运行。设置页内可离线查看关于、隐私和许可。

原项目与智谱、微信等商标仅用于来源和兼容性说明，不代表官方背书。上游 `docs/KICKOFF.md` 和旧截图为历史资料，实际行为以本分支代码与测试说明为准。
