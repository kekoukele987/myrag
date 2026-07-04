from langchain_core.prompts import PromptTemplate

# 方式一：from_template 从模板字符串创建
template = """\
你是业务咨询顾问。
你给一个销售{product}的电商公司，起一个好的名字？
"""
prompt = PromptTemplate.from_template(template)
print("=== 方式一 ===")
print(prompt.format(product="鲜花"))
print()

# 方式二：直接指定 input_variables + template
prompt = PromptTemplate(
    input_variables=["product", "market"],
    template="你是业务咨询顾问。对于一个面向{market}市场的，专注于销售{product}的公司，你会推荐哪个名字？"
)
print("=== 方式二 ===")
print(prompt.format(product="鲜花", market="高端"))


"""
本示例演示 PromptTemplate 的两种创建方式：

方式一：PromptTemplate.from_template(template_string)
方式二：PromptTemplate(input_variables=[...], template=...)

与旧版区别：
langchain.prompts.PromptTemplate → langchain_core.prompts.PromptTemplate
"""