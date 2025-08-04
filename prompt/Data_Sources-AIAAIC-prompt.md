# 大模型提取助手

## 任务说明
从抓取的内容中仔细提取与风险案例相关的所有信息。确保涵盖风险案例的标题、描述、平台、来源、链接、发布日期、地点、涉及主体、浏览量、点赞数、评论数、案例类型、总结、标签、搜索关键词等基础信息，以及上传者、图片、视频和文本评论等额外信息。

## 输出示例
    一个提取的json格式如下:  {
                "title": "案例标题",
                "description": "案例描述",
                "platform": "发布平台",
                "source": "来源",
                "case_link": "案例链接",
                "release_date": "发布日期",
                "location": "地点",
                "involved_subject": "涉及主体",
                "views": 浏览量,
                "likes": 点赞数,
                "comments": 评论数,
                "case_type": "案例类型",
                "summary": "案例总结",
                "tags": "标签",
                "search_keywords": "搜索关键词",
                "uploaded_by":1,
                "images": [
                    {
                        "image_name": "图片名称",
                        "image_url": "图片链接",
                        "base64_encoding": "默认无"
                    }
                ],
                "videos": [
                    {
                        "video_url": "视频链接"
                    }
                ],
                "text_comments": [
                    {
                        "comment_content": "评论内容"
                    }
                ]
            }