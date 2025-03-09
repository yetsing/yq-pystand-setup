# yq-pystand-setup

python 脚本工具

自动创建一个使用 [PyStand](https://github.com/skywind3000/PyStand) 的项目

它会在 PyStand 的基础上，自动安装 pip 。

# 安装

```
pip install yq-pystand-setup
```

# 使用

## 创建项目

```
py -m yq_pystand_setup [Project Name]
```

## 已有项目初始化

```
py -m yq_pystand_setup --init /path/to/project
```

## 安装包

首先激活环境

进入项目目录下，执行

### Activate in cmd

```
call activate.cmd
```

### Activate in Powershell

```
. activate.ps1
```

激活之后 python pip 都会指向项目使用的，如下所示

```
$ Get-Command python | Format-List -Property path
Path : D:\path\to\your\project\runtime\python.exe

$ Get-Command pip | Format-List -Property Path
Path : D:\path\to\your\project\runtime\pip_wrapper\bin\pip.exe
```

然后正常使用 pip 安装，例如

```
pip install flask
```

# PyCharm 配置

手动将项目下的 runtime/Lib/site-packages 标记为 Sources Root ，不然识别不了你安装在这里的包

解析器直接选择 runtime/python.exe

因为我们放了一些 activate 开头的空文件在 runtime ， PyCharm 会将它识别为当前项目的 virtualenv

# 参考

[PyStand](https://github.com/skywind3000/PyStand)

[Portable Python Bundles on Windows](https://dev.to/treehouse/portable-python-bundles-on-windows-41ac)

# 实现

1. 在当前目录下创建项目文件夹
2. 安装 PyStand （PyStand-py38-x64.7z）
3. 安装 pip
4. 其他设置（放一些空文件，让 PyCharm 认为这是一个 vritualenv）
