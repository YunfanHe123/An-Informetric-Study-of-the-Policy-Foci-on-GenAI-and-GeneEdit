import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 配置浏览器选项
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 无头模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 初始化浏览器
driver = webdriver.Chrome(options=options)


def login_overton(driver):
    # 第一步：输入邮箱
    driver.get("https://app.overton.io/ui/auth/login")

    # 输入邮箱（更稳定的定位方式）
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='eg. user@institution.co']"))
    )
    email_input.send_keys("24110170045@m.fudan.edu.cn")

    # 点击Next按钮
    next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
    next_button.click()

    # 第二步：输入密码（关键修改部分）
    # 使用XPath精准定位密码输入框
    password_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
    )
    password_input.send_keys("heyunfan410803")

    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, "//button[contains(.,'Log in')]")
    login_button.click()

    # 验证登录成功
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//header[contains(@class,'app-header')]"))
    )
    print("登录成功！")

# 数据提取函数
def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # 提取长摘要
    long_abstract = ""
    for section in soup.find_all("div", class_="document_description--section"):
        if section.find("h4", class_="document_description--section-title", string="Document description"):
            long_abstract = section.get_text(strip=True).replace("Document description", "").strip()
            break

    # 提取短摘要
    short_abstract = ""
    snippet = soup.find("div", class_="editable snippet")
    if snippet:
        short_abstract = snippet.get_text(strip=True)

    # 提取关键词
    keywords = []
    tags_div = soup.find("div", class_="tags")
    if tags_div:
        for tag in tags_div.find_all("a"):
            keywords.append(tag.get_text(strip=True))

    return {
        "long_abstract": long_abstract,
        "short_abstract": short_abstract,
        "keywords": "; ".join(keywords)
    }


# 主程序
def main():
    try:
        # 登录
        login_overton(driver)

        # 读取CSV文件
        df = pd.read_csv("E:\input.csv",encoding='gbk')
        results = []

        # 遍历每个URL
        for index, row in df.iterrows():
            try:
                print(f"正在处理文档 {index + 1}/{len(df)}: {row['Policy_document_id']}")

                driver.get(row["Overton URL"])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "document_description--section"))
                )

                # 提取数据
                data = extract_data(driver.page_source)
                data.update({
                    "Policy_document_id": row["Policy_document_id"],
                    "URL": row["Overton URL"]
                })
                results.append(data)

                time.sleep(2)  # 礼貌性等待

            except Exception as e:
                print(f"处理文档 {row['Policy_document_id']} 时出错: {str(e)}")
                continue

        # 保存结果
        result_df = pd.DataFrame(results)
        result_df.to_csv("E:\overton_results.csv", index=False)
        print("数据抓取完成！结果已保存到 overton_results.csv")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()