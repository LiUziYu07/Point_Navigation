# Vision-Language Navigation
## 项目结构

```bash
├─config                 # 配置相关文件
├─core                   # 核心模块
│  ├─flagged             # 标记的数据
├─data                   # 数据存储
│  ├─obs                 # 实时观测数据
│  ├─outdated            # 过时数据
│  ├─results             # 结果数据
│  └─samples             # 样本数据
├─download               # 下载模块
├─fusion                 # 数据融合模块
├─graph                  # 图处理模块
├─keypoint_detector      # 关键点检测模块
│  ├─disk                # 使用 DISK 方法的关键点检测
├─llm                    # 大语言模型相关模块
├─perception             # 感知模块
│  ├─GroundingDINO       # GroundingDINO 相关代码
├─prompt                 # 提示相关文件
├─script                 # 脚本文件
└─utils                  # 工具函数

```
## 模块说明
### config
包含项目的配置文件以及缓存文件。

### core
核心模块，包括标记和处理相关核心功能。

### data
存储项目数据，分为以下几类：
    obs：实时观测数据（图像、JSON 和点云数据）。
    outdated：过时的处理数据。
    results：处理结果。
    samples：项目样本数据。 

### download
由于无法直接获取ROS的图像、ACML、点云等数据，通过ssh从tracer中的文件夹获取数据

### fusion
实现点云数据与RGB图像的融合

### graph
点对点导航、物体目标导航中的拓扑图的建立与维护


### keypoint_detector
为了IIN(Instance Image Goal Navigation)准备的
关键点检测模块，支持 DISK 和其他子模块。

### llm
与大语言模型（LLM）相关的功能模块。

### perception
感知模块，包含 GroundingDINO 的实现和模型文件。

### prompt
处理与提示（prompt）相关的任务。

### script
项目使用的脚本文件，例如删除outdated文件夹中的文件

### utils
工具类和辅助函数，雷达坐标系到相机坐标系、相机坐标系到图像坐标系的变换、

多线程的开启

读取yaml文件

图像去畸

## 使用说明
```bash
pip install -r requirements.txt
```

## 第三方依赖
https://github.com/facebookresearch/segment-anything
https://github.com/IDEA-Research/GroundingDINO
https://github.com/cvlab-epfl/disk