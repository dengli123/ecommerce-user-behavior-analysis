# 如何把项目上传到 GitHub（小白版）

按下面做，大约 10 分钟就能拿到可写进简历的项目链接。

---

## 一、准备工作

1. 打开 [https://github.com](https://github.com) 注册/登录账号  
2. 你电脑已安装 Git（你这边已安装：`git version 2.54.0`）  
3. 项目已在桌面：  
   `C:\Users\邓颖泽\Desktop\ecommerce-user-behavior-analysis`

---

## 二、在 GitHub 上新建仓库

1. 登录 GitHub → 右上角 `+` → `New repository`
2. Repository name 填：`ecommerce-user-behavior-analysis`
3. 描述可写：`电商用户消费行为数据分析（Python + SQL + RFM）`
4. 选择 **Public**（公开，方便简历展示）
5. **不要**勾选 “Add a README file”（本地已有 README）
6. 点击 `Create repository`

创建后页面会显示仓库地址，类似：

```text
https://github.com/你的用户名/ecommerce-user-behavior-analysis.git
```

把这个地址复制下来。

---

## 三、本地上传（推荐命令）

打开 **PowerShell** 或 **CMD**，依次执行：

```bash
cd C:\Users\邓颖泽\Desktop\ecommerce-user-behavior-analysis

git init
git add .
git commit -m "feat: 完成电商用户行为数据分析项目"

git branch -M main
git remote add origin https://github.com/你的用户名/ecommerce-user-behavior-analysis.git
git push -u origin main
```

### 说明

- 把 `你的用户名` 换成你的 GitHub 用户名  
- 第一次 `git push` 可能会弹出登录窗口  
  - 推荐用 **GitHub 登录 / Personal Access Token**  
  - 如果提示要 Token：GitHub → Settings → Developer settings → Personal access tokens → 生成 token（勾选 `repo`）

---

## 四、上传成功后你会得到

项目主页链接（写进简历）：

```text
https://github.com/你的用户名/ecommerce-user-behavior-analysis
```

---

## 五、简历里怎么写链接

在项目经历最后加一行：

```text
项目地址：https://github.com/你的用户名/ecommerce-user-behavior-analysis
```

---

## 六、常见问题

### 1. `git` 不是内部或外部命令
说明 Git 没装好或没进 PATH。重新安装 Git for Windows，安装时勾选 “Add to PATH”。

### 2. `failed to push` / 权限错误
- 检查仓库地址是否正确  
- 确认已登录 GitHub  
- 用 Personal Access Token 代替密码

### 3. 文件太大推不上去
本项目已在 `.gitignore` 忽略了百万级 CSV/数据库文件，一般不会超限。  
如果仍失败，确认没有手动 `git add` 大文件。

### 4. 想更新代码后再上传

```bash
cd C:\Users\邓颖泽\Desktop\ecommerce-user-behavior-analysis
git add .
git commit -m "update: 优化分析报告"
git push
```

---

## 七、面试前建议你自己再做一遍

虽然项目代码已可运行，但面试可能问：

1. 你怎么清洗异常值？  
2. RFM 三个指标分别是什么？  
3. 三类用户怎么划分？  
4. 两条运营建议依据是什么？  

请至少打开并阅读：

- `scripts/02_clean_data.py`
- `scripts/03_sql_analysis.py`
- `scripts/04_rfm_and_visualize.py`
- `output/reports/analysis_report.md`

能讲清楚，比“有没有 GitHub 链接”更重要。
