"""错误定义模块

本模块定义了cc-tool项目中使用的所有自定义异常。
"""


class CCToolError(Exception):
    """所有cc-tool异常的基类"""
    pass


class ProjectDirectoryError(CCToolError):
    """项目目录相关错误"""
    pass


class LanguageNotSupportedError(CCToolError):
    """语言不支持错误"""
    pass


class TemplateNotFoundError(CCToolError):
    """模板不存在错误"""
    pass


class FileOperationError(CCToolError):
    """文件操作错误"""
    pass


class VariableReplaceError(CCToolError):
    """变量替换错误"""
    pass


class GitignoreError(CCToolError):
    """.gitignore操作错误"""
    pass


class UserConfigError(CCToolError):
    """用户配置错误"""
    pass