"""
本地透视表BI看板

功能：
1. 读取本地数据文件（CSV、TXT、XLS、XLSX）
2. 自动识别字段类型（文本、数值、日期时间、布尔）
3. 生成透视表并支持多种汇总方式
4. 提供多种数据可视化图表
5. 支持数据导出和本地保存

作者：Auto-GPT
日期：2026-02-27
"""

import io
import os
import re
import pandas as pd
import time

import streamlit as st
import altair as alt

# 设置页面配置
st.set_page_config(page_title="本地透视表BI看板", layout="wide")

@st.cache_data(show_spinner=False)
def read_table(file_bytes, filename, sheet_name=None):
    """
    读取表格文件并进行预处理
    
    参数：
        file_bytes: 文件字节数据
        filename: 文件名
        sheet_name: Excel工作表名称或索引
    
    返回：
        预处理后的DataFrame
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".xls", ".xlsx"]:
        bio = io.BytesIO(file_bytes)
        df = pd.read_excel(bio, sheet_name=sheet_name if sheet_name is not None else 0, dtype=str, engine="openpyxl")
    elif ext in [".csv", ".txt"]:
        bio = io.BytesIO(file_bytes)
        # 尝试不同的编码格式
        encodings = ["utf-8", "gbk", "gb2312", "utf-16"]
        df = None
        for encoding in encodings:
            try:
                bio.seek(0)  # 重置文件指针
                df = pd.read_csv(bio, dtype=str, encoding=encoding, header=0)
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            # 如果所有编码都失败，使用errors='replace'模式
            bio.seek(0)
            df = pd.read_csv(bio, dtype=str, encoding="utf-8", errors="replace", header=0)
    else:
        raise ValueError("仅支持csv/txt/xlsx/xls")
    
    # 预处理：清理列名、处理空值
    df.columns = [str(c).strip() for c in df.columns]
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    return df

def is_long_int_string(s):
    """
    检查字符串是否为长整数（13位以上）
    
    参数：
        s: 要检查的字符串
    
    返回：
        bool: 是否为长整数
    """
    if s is None or pd.isna(s):
        return False
    return re.fullmatch(r"[+-]?\d{13,}", str(s).strip()) is not None

def is_numeric_string(s):
    """
    检查字符串是否为数值
    
    参数：
        s: 要检查的字符串
    
    返回：
        bool: 是否为数值
    """
    if s is None or pd.isna(s):
        return False
    return re.fullmatch(r"[+-]?\d+(\.\d+)?", str(s).strip()) is not None

def infer_types_and_convert(df):
    """
    推断字段类型并进行转换
    
    参数：
        df: 输入的DataFrame
    
    返回：
        tuple: (转换后的DataFrame, 字段类型映射)
    """
    type_map = {}
    out = df.copy()
    for col in out.columns:
        s = out[col]
        # 检查是否包含长整数（13位以上）
        if s.dropna().astype(str).map(is_long_int_string).any():
            type_map[col] = "text"
            out[col] = s.astype(str)
            continue
        
        s_str = s.astype(str)
        s_nonempty = s_str[~s_str.isna() & (s_str.str.strip() != "")]
        
        # 检查是否为布尔类型
        if not s_nonempty.empty:
            bool_values = {'true', 'false', 'yes', 'no', '1', '0'}
            bool_mask = s_nonempty.str.lower().isin(bool_values)
            if bool_mask.all():
                out[col] = s_nonempty.str.lower().map({'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False})
                type_map[col] = "boolean"
                continue
        
        # 尝试推断日期时间类型
        if not s_nonempty.empty:
            dt_try = pd.to_datetime(s_nonempty, errors="coerce", infer_datetime_format=True)
            dt_ratio = float(dt_try.notna().sum()) / float(len(s_nonempty))
        else:
            dt_ratio = 0.0
        if dt_ratio >= 0.8:  # 降低阈值以提高日期识别率
            # 转换为日期时间类型并统一格式
            out[col] = pd.to_datetime(s_str, errors="coerce", infer_datetime_format=True)
            # 确保日期格式统一为yyyy-mm-dd
            out[col] = pd.to_datetime(out[col].dt.strftime('%Y-%m-%d'), errors="coerce")
            type_map[col] = "datetime"
            continue
        
        # 尝试推断数值类型
        num_mask = s_nonempty.map(is_numeric_string)
        if not s_nonempty.empty and num_mask.all():
            out[col] = pd.to_numeric(s_str, errors="coerce")
            type_map[col] = "number"
            continue
        
        # 默认按文本处理
        type_map[col] = "text"
        out[col] = s_str
    return out, type_map

def build_pivot(df, rows, cols, value_col, agg):
    """
    生成透视表
    
    参数：
        df: 输入的DataFrame
        rows: 行字段列表
        cols: 列字段列表
        value_col: 值字段
        agg: 汇总方式
    
    返回：
        生成的透视表DataFrame
    """
    # 限制数据量，提高性能
    max_rows = 100000
    if len(df) > max_rows:
        st.warning(f"数据量较大（{len(df)}行），将使用前{max_rows}行进行处理以提高性能")
        df = df.head(max_rows)
    
    if value_col:
        aggfunc = {"sum": "sum", "avg": "mean", "count": "count", "min": "min", "max": "max"}[agg]
        try:
            pv = pd.pivot_table(df, index=rows if rows else None, columns=cols if cols else None, values=value_col, aggfunc=aggfunc, dropna=False, margins=False)
        except Exception as e:
            # 如果透视表生成失败，返回简化版
            st.warning(f"透视表生成失败：{str(e)}，将使用简化版结果")
            pv = df.groupby(rows)[value_col].agg(aggfunc).to_frame() if rows else pd.DataFrame({agg: [df[value_col].agg(aggfunc)]})
    else:
        try:
            pv = df.value_counts(subset=rows).to_frame("count") if rows else pd.DataFrame({"count": [len(df)]})
        except Exception as e:
            st.warning(f"计数失败：{str(e)}，将使用简化版结果")
            pv = pd.DataFrame({"count": [len(df)]})
    
    if isinstance(pv.index, pd.MultiIndex):
        pv = pv.sort_index()
    return pv

def pivot_to_tidy(pv):
    """
    将透视表转换为tidy格式
    
    参数：
        pv: 透视表DataFrame
    
    返回：
        tidy格式的DataFrame
    """
    try:
        if isinstance(pv, pd.Series):
            pv = pv.to_frame()
        
        if pv.empty:
            return pd.DataFrame({"系列": [], "值": []})
        
        pv_reset = pv.reset_index()
        value_name = pv_reset.columns[-1] if pv_reset.columns[-1] not in pv.columns else "value"
        
        if hasattr(pv, "columns") and isinstance(pv.columns, pd.MultiIndex):
            pv_reset.columns = ["/".join([str(x) for x in c if str(x) != ""]) for c in pv_reset.columns]
            tidy = pv_reset.melt(id_vars=pv_reset.columns[:-1], var_name="系列", value_name="值")
        elif hasattr(pv, "columns") and pv.columns.size > 1:
            tidy = pv_reset.melt(id_vars=pv_reset.columns[:-pv.columns.size], var_name="系列", value_name="值")
        else:
            tidy = pv_reset.rename(columns={pv_reset.columns[-1]: "值"})
            tidy["系列"] = "总计"
        
        return tidy
    except Exception as e:
        st.warning(f"数据转换失败：{str(e)}，将使用空数据框")
        return pd.DataFrame({"系列": [], "值": []})

def save_to_local(data, filename, output_dir=None):
    """
    保存数据到本地文件
    
    参数：
        data: 要保存的数据（DataFrame或bytes）
        filename: 保存的文件名
        output_dir: 输出目录，默认为当前工作目录
    
    返回：
        保存的文件路径
    """
    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    if isinstance(data, pd.DataFrame):
        data.to_csv(file_path, index=True, encoding="utf-8-sig")
    elif isinstance(data, bytes):
        with open(file_path, "wb") as f:
            f.write(data)
    return file_path

st.title("本地透视表BI看板")
st.caption("读取本地透视表，自动识别字段类型；超过12位的数字字段按文本处理。")

tab1, tab2 = st.tabs(["数据源", "看板"])
with tab1:
    st.header("📁 数据源上传")
    st.caption("支持CSV、TXT、XLS、XLSX格式文件")
    
    col1, col2 = st.columns(2)
    with col1:
        up = st.file_uploader("选择本地文件", type=["csv", "txt", "xlsx", "xls"], help="点击上传本地数据文件")
    with col2:
        path = st.text_input("或输入本地文件路径", help="直接输入文件的完整路径")
    
    sheet = None
    loaded = None
    if up is not None:
        loaded = ("upload", up.name, up.getvalue())
    elif path:
        if os.path.exists(path):
            sheet = st.text_input("如为Excel可指定工作表名或索引", value="", help="留空则使用第一个工作表")
            sheet_name = int(sheet) if sheet.isdigit() else (sheet if sheet else None)
            with open(path, "rb") as f:
                loaded = ("path", os.path.basename(path), f.read())
        else:
            st.error("文件不存在")
    
    if loaded:
        try:
            start_time = time.time()
            with st.spinner("正在加载文件..."):
                origin_df = read_table(loaded[2], loaded[1], sheet_name if 'sheet_name' in locals() else None)
                df, type_map = infer_types_and_convert(origin_df)
            load_time = time.time() - start_time
            st.session_state["df"] = df
            st.session_state["type_map"] = type_map
            
            st.success(f"✅ 已加载：{loaded[1]}，行数：{len(df)}，列数：{len(df.columns)}，加载时间：{load_time:.2f}秒")
            
            st.subheader("📋 数据预览")
            st.caption("显示前50行数据")
            st.dataframe(df.head(50), use_container_width=True)
            
            st.subheader("🔍 字段类型")
            st.caption("自动识别的字段类型")
            schema = pd.DataFrame([{"字段": k, "类型": v} for k, v in type_map.items()])
            st.dataframe(schema, use_container_width=True)
        except Exception as e:
            st.error(f"❌ 加载文件失败：{str(e)}")

with tab2:
    if "df" not in st.session_state:
        st.info("请先在“数据源”选项卡加载文件")
    else:
        df = st.session_state["df"]
        type_map = st.session_state["type_map"]
        dims = [c for c, t in type_map.items() if t in ["text", "datetime", "boolean"]]
        nums = [c for c, t in type_map.items() if t == "number"]
        
        with st.sidebar:
            st.header("🎯 数据筛选")
            st.caption("设置数据筛选条件")
            
            # 日期区间筛选
            date_cols = [c for c, t in type_map.items() if t == "datetime"]
            if date_cols:
                selected_date_col = st.selectbox("选择日期字段", date_cols, help="选择用于筛选的日期字段")
                # 获取日期范围
                min_date = df[selected_date_col].min()
                max_date = df[selected_date_col].max()
                
                if pd.notna(min_date) and pd.notna(max_date):
                    start_date = st.date_input("开始日期", min_value=min_date, max_value=max_date, value=min_date, help="选择筛选的开始日期")
                    end_date = st.date_input("结束日期", min_value=min_date, max_value=max_date, value=max_date, help="选择筛选的结束日期")
                else:
                    start_date = st.date_input("开始日期", help="选择筛选的开始日期")
                    end_date = st.date_input("结束日期", help="选择筛选的结束日期")
            else:
                selected_date_col = None
                start_date = None
                end_date = None
            
            # 条件筛选
            st.subheader("条件筛选")
            filter_conditions = []
            num_conditions = st.number_input("筛选条件数量", min_value=0, max_value=5, value=0, step=1, help="设置筛选条件的数量")
            
            for i in range(num_conditions):
                with st.expander(f"筛选条件 {i+1}"):
                    filter_field = st.selectbox(f"选择字段 {i+1}", list(df.columns), key=f"filter_field_{i}", help="选择需要筛选的字段")
                    field_type = type_map.get(filter_field, "text")
                    
                    if field_type == "number":
                        filter_op = st.selectbox(f"操作符 {i+1}", ["=", "<", "<=", ">", ">=", "!="], key=f"filter_op_{i}")
                        filter_value = st.number_input(f"值 {i+1}", key=f"filter_value_{i}")
                    elif field_type == "datetime":
                        filter_op = st.selectbox(f"操作符 {i+1}", ["=", "<", "<=", ">", ">="], key=f"filter_op_{i}")
                        filter_value = st.date_input(f"值 {i+1}", key=f"filter_value_{i}")
                    else:
                        filter_op = st.selectbox(f"操作符 {i+1}", ["=", "!=", "包含", "不包含"], key=f"filter_op_{i}")
                        filter_value = st.text_input(f"值 {i+1}", key=f"filter_value_{i}")
                    
                    filter_conditions.append((filter_field, filter_op, filter_value))
            
            st.divider()
            
            st.header("📊 透视设置")
            st.caption("选择字段和汇总方式")
            rows = st.multiselect("行字段", dims, help="选择作为行维度的字段")
            cols = st.multiselect("列字段", [d for d in dims if d not in rows], help="选择作为列维度的字段")
            agg = st.selectbox("汇总方式", ["sum", "avg", "count", "min", "max"], index=0, help="选择数值字段的汇总方式")
            
            st.divider()
            
            st.header("🔧 自定义字段")
            st.caption("创建新的计算字段")
            
            # 自定义字段设置
            custom_fields = []
            num_custom_fields = st.number_input("自定义字段数量", min_value=0, max_value=5, value=0, step=1)
            
            for i in range(num_custom_fields):
                with st.expander(f"自定义字段 {i+1}"):
                    field_name = st.text_input(f"字段名称 {i+1}", key=f"custom_name_{i}")
                    formula = st.text_input(f"计算公式 {i+1}", key=f"custom_formula_{i}", 
                                         help="使用字段名进行计算，例如：花费/观看人数")
                    if field_name and formula:
                        custom_fields.append((field_name, formula))
            
            st.divider()
            
            st.header("💾 本地输出设置")
            st.caption("设置本地保存选项")
            output_dir = st.text_input("输出目录", value=os.getcwd(), help="设置保存文件的目录路径")
            save_local = st.checkbox("保存到本地", help="勾选后将结果保存到本地文件")
            
            st.divider()
            
            st.header("ℹ️ 帮助信息")
            st.info("- 行字段和列字段用于分组数据\n- 值字段用于数值汇总\n- 支持多种图表类型可视化\n- 超过10万行的数据会自动采样")
        
        # 应用筛选条件
        filtered_df = df.copy()
        
        # 应用日期区间筛选
        if selected_date_col and start_date and end_date:
            try:
                # 确保日期格式匹配
                start_date_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
                end_date_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
                filtered_df = filtered_df[(
                    pd.to_datetime(filtered_df[selected_date_col]).dt.strftime('%Y-%m-%d') >= start_date_str
                ) & (
                    pd.to_datetime(filtered_df[selected_date_col]).dt.strftime('%Y-%m-%d') <= end_date_str
                )]
                st.success(f"✅ 日期筛选成功，筛选后数据行数：{len(filtered_df)}")
            except Exception as e:
                st.error(f"❌ 日期筛选失败：{str(e)}")
        
        # 应用条件筛选
        for field, op, value in filter_conditions:
            try:
                field_type = type_map.get(field, "text")
                
                if field_type == "number":
                    if op == "=":
                        filtered_df = filtered_df[filtered_df[field] == value]
                    elif op == "<":
                        filtered_df = filtered_df[filtered_df[field] < value]
                    elif op == "<=":
                        filtered_df = filtered_df[filtered_df[field] <= value]
                    elif op == ">":
                        filtered_df = filtered_df[filtered_df[field] > value]
                    elif op == ">=":
                        filtered_df = filtered_df[filtered_df[field] >= value]
                    elif op == "!=":
                        filtered_df = filtered_df[filtered_df[field] != value]
                
                elif field_type == "datetime":
                    value_date = pd.to_datetime(value)
                    if op == "=":
                        filtered_df = filtered_df[pd.to_datetime(filtered_df[field]).dt.date == value_date.date()]
                    elif op == "<":
                        filtered_df = filtered_df[pd.to_datetime(filtered_df[field]).dt.date < value_date.date()]
                    elif op == "<=":
                        filtered_df = filtered_df[pd.to_datetime(filtered_df[field]).dt.date <= value_date.date()]
                    elif op == ">":
                        filtered_df = filtered_df[pd.to_datetime(filtered_df[field]).dt.date > value_date.date()]
                    elif op == ">=":
                        filtered_df = filtered_df[pd.to_datetime(filtered_df[field]).dt.date >= value_date.date()]
                
                else:  # text and boolean
                    value_str = str(value)
                    if op == "=":
                        filtered_df = filtered_df[filtered_df[field].astype(str) == value_str]
                    elif op == "!=":
                        filtered_df = filtered_df[filtered_df[field].astype(str) != value_str]
                    elif op == "包含":
                        filtered_df = filtered_df[filtered_df[field].astype(str).str.contains(value_str, na=False)]
                    elif op == "不包含":
                        filtered_df = filtered_df[~filtered_df[field].astype(str).str.contains(value_str, na=False)]
                
            except Exception as e:
                st.error(f"❌ 条件筛选失败：{str(e)}")
        
        # 处理自定义字段
        df_with_custom = filtered_df.copy()
        type_map_with_custom = type_map.copy()
        custom_field_formulas = {}
        
        # 先收集自定义字段信息，但不立即计算
        for field_name, formula in custom_fields:
            try:
                custom_field_formulas[field_name] = formula
                type_map_with_custom[field_name] = "number"
                st.success(f"✅ 成功创建自定义字段：{field_name}")
            except Exception as e:
                st.error(f"❌ 创建自定义字段 {field_name} 失败：{str(e)}")
        
        # 更新维度和数值字段列表
        dims_with_custom = [c for c, t in type_map_with_custom.items() if t in ["text", "datetime", "boolean"]]
        nums_with_custom = [c for c, t in type_map_with_custom.items() if t == "number"]
        
        # 在主界面添加值字段选择（包含自定义字段）
        st.subheader("🔧 字段设置")
        value_col = st.selectbox("值字段", [""] + nums_with_custom, index=0 if not nums_with_custom else 1, help="选择需要汇总的数值字段")
        
        # 主内容区域
        st.header("📈 数据分析看板")
        
        # 数据概览模块
        st.subheader("📋 数据概览")
        try:
            with st.spinner("正在生成数据概览..."):
                # 基本统计信息
                st.caption("数据基本信息")
                overview_cols = st.columns(4)
                with overview_cols[0]:
                    st.metric("总数据量", f"{len(filtered_df)} 行")
                with overview_cols[1]:
                    st.metric("字段数量", f"{len(filtered_df.columns)} 个")
                with overview_cols[2]:
                    num_cols = len([c for c, t in type_map.items() if t == "number"])
                    st.metric("数值字段", f"{num_cols} 个")
                with overview_cols[3]:
                    date_cols = len([c for c, t in type_map.items() if t == "datetime"])
                    st.metric("日期字段", f"{date_cols} 个")
                
                # 数值字段统计
                num_fields = [c for c, t in type_map.items() if t == "number"]
                if num_fields:
                    st.caption("数值字段统计")
                    stats_df = filtered_df[num_fields].describe().T
                    stats_df = stats_df[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
                    st.dataframe(stats_df, use_container_width=True)
                
                # 文本字段统计
                text_fields = [c for c, t in type_map.items() if t == "text"]
                if text_fields:
                    st.caption("文本字段统计")
                    text_stats = []
                    for field in text_fields:
                        unique_count = filtered_df[field].nunique()
                        non_null_count = filtered_df[field].notna().sum()
                        text_stats.append({"字段": field, "非空值": non_null_count, "唯一值": unique_count})
                    text_stats_df = pd.DataFrame(text_stats)
                    st.dataframe(text_stats_df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ 生成数据概览失败：{str(e)}")
        
        # 数据质量分析模块
        st.subheader("🔍 数据质量分析")
        try:
            with st.spinner("正在分析数据质量..."):
                # 缺失值分析
                st.caption("缺失值分析")
                missing_data = []
                for col in filtered_df.columns:
                    missing_count = filtered_df[col].isna().sum()
                    missing_ratio = missing_count / len(filtered_df) * 100
                    missing_data.append({"字段": col, "缺失值数量": missing_count, "缺失率": f"{missing_ratio:.2f}%"})
                missing_df = pd.DataFrame(missing_data)
                st.dataframe(missing_df, use_container_width=True)
                
                # 重复值分析
                st.caption("重复值分析")
                duplicate_rows = filtered_df.duplicated().sum()
                duplicate_ratio = duplicate_rows / len(filtered_df) * 100
                st.info(f"重复行数：{duplicate_rows}，重复率：{duplicate_ratio:.2f}%")
                
                # 异常值检测（基于IQR方法）
                st.caption("数值字段异常值检测")
                outlier_data = []
                for field in num_fields:
                    if field in filtered_df.columns:
                        Q1 = filtered_df[field].quantile(0.25)
                        Q3 = filtered_df[field].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outliers = filtered_df[(filtered_df[field] < lower_bound) | (filtered_df[field] > upper_bound)]
                        outlier_count = len(outliers)
                        outlier_ratio = outlier_count / len(filtered_df) * 100
                        outlier_data.append({"字段": field, "异常值数量": outlier_count, "异常率": f"{outlier_ratio:.2f}%", "正常范围": f"[{lower_bound:.2f}, {upper_bound:.2f}]"})
                if outlier_data:
                    outlier_df = pd.DataFrame(outlier_data)
                    st.dataframe(outlier_df, use_container_width=True)
                else:
                    st.info("没有数值字段可进行异常值检测")
        except Exception as e:
            st.error(f"❌ 数据质量分析失败：{str(e)}")
        
        # 透视表部分
        st.subheader("📊 透视结果")
        try:
            start_time = time.time()
            with st.spinner("正在生成透视表..."):
                # 检查值字段是否是自定义字段
                if value_col and value_col in custom_field_formulas:
                    # 解析自定义字段公式
                    formula = custom_field_formulas[value_col]
                    
                    # 提取公式中的字段名
                    import re
                    field_names = re.findall(r'\b(\w+)\b', formula)
                    # 过滤出实际存在的字段
                    actual_fields = [f for f in field_names if f in filtered_df.columns]
                    
                    if not actual_fields:
                        st.error(f"❌ 自定义字段 {value_col} 的公式中没有有效的字段")
                        pv = pd.DataFrame()
                    else:
                        # 为每个基础字段生成透视表（使用sum聚合）
                        base_pivots = {}
                        for field in actual_fields:
                            base_pivots[field] = build_pivot(filtered_df, rows, cols, field, "sum")
                        
                        # 合并基础透视表
                        if rows or cols:
                            # 找到所有索引和列的组合
                            index_cols = []
                            if rows:
                                index_cols.extend(rows)
                            if cols:
                                index_cols.extend(cols)
                            
                            # 创建基础数据框
                            combined_df = None
                            for field, base_pv in base_pivots.items():
                                if combined_df is None:
                                    combined_df = base_pv.reset_index()
                                    combined_df = combined_df.rename(columns={combined_df.columns[-1]: field})
                                else:
                                    temp_df = base_pv.reset_index()
                                    temp_df = temp_df.rename(columns={temp_df.columns[-1]: field})
                                    combined_df = pd.merge(combined_df, temp_df, on=index_cols, how="outer")
                            
                            # 计算自定义字段
                            for field in actual_fields:
                                formula = formula.replace(field, f"combined_df['{field}']")
                            
                            combined_df[value_col] = eval(formula)
                            
                            # 重建透视表
                            if rows and cols:
                                pv = combined_df.pivot(index=rows, columns=cols, values=value_col)
                            elif rows:
                                pv = combined_df.set_index(rows)[[value_col]]
                            elif cols:
                                pv = combined_df.pivot(columns=cols, values=value_col)
                            else:
                                # 只有一个值
                                pv = pd.DataFrame({value_col: [combined_df[value_col].iloc[0]]})
                        else:
                            # 没有行和列字段，直接计算
                            base_values = {}
                            for field in actual_fields:
                                base_values[field] = df[field].sum()
                            
                            # 计算自定义字段
                            formula_with_values = formula
                            for field, value in base_values.items():
                                formula_with_values = formula_with_values.replace(field, str(value))
                            
                            result = eval(formula_with_values)
                            pv = pd.DataFrame({value_col: [result]})
                else:
                    # 普通字段，直接生成透视表
                    pv = build_pivot(df_with_custom, rows, cols, value_col if value_col else None, agg)
            build_time = time.time() - start_time
            
            st.info(f"⏱️ 透视表生成时间：{build_time:.2f}秒")
            st.dataframe(pv, use_container_width=True)
            tidy = pivot_to_tidy(pv)
        except Exception as e:
            st.error(f"❌ 生成透视表失败：{str(e)}")
            tidy = pd.DataFrame()
        
        # 可视化部分
        st.subheader("🎨 数据可视化")
        chart_type = st.selectbox("图表类型", ["柱状图", "折线图", "饼图", "散点图"])
        x_field = rows[0] if rows else (df.columns[0] if len(df.columns) else None)
        try:
            if x_field is not None and "值" in tidy.columns and not tidy.empty:
                if "系列" not in tidy.columns:
                    tidy["系列"] = "总计"
                
                if chart_type == "柱状图":
                    ch = alt.Chart(tidy).mark_bar().encode(
                        x=alt.X(f"{x_field}:N", sort=None, title=x_field),
                        y=alt.Y("值:Q", title="值"),
                        color=alt.Color("系列:N", title="系列"),
                        tooltip=list(tidy.columns)
                    ).properties(
                        title=f"{x_field} 数据分布"
                    )
                elif chart_type == "折线图":
                    ch = alt.Chart(tidy).mark_line(point=True).encode(
                        x=alt.X(f"{x_field}:N", sort=None, title=x_field),
                        y=alt.Y("值:Q", title="值"),
                        color=alt.Color("系列:N", title="系列"),
                        tooltip=list(tidy.columns)
                    ).properties(
                        title=f"{x_field} 趋势变化"
                    )
                elif chart_type == "饼图":
                    # 饼图需要聚合数据
                    pie_data = tidy.groupby("系列").agg({"值": "sum"}).reset_index()
                    ch = alt.Chart(pie_data).mark_arc().encode(
                        theta=alt.Theta("值:Q", title="值"),
                        color=alt.Color("系列:N", title="系列"),
                        tooltip=["系列", "值"]
                    ).properties(
                        title="数据分布饼图",
                        width=400,
                        height=400
                    )
                elif chart_type == "散点图":
                    # 散点图需要两个数值字段
                    if len(nums) >= 2:
                        y_field = st.selectbox("Y轴字段", nums, index=1)
                        ch = alt.Chart(df).mark_point().encode(
                            x=alt.X(f"{x_field}:Q", title=x_field),
                            y=alt.Y(f"{y_field}:Q", title=y_field),
                            color=alt.Color("系列:N", title="系列") if "系列" in tidy.columns else None,
                            tooltip=list(df.columns)
                        ).properties(
                            title=f"{x_field} vs {y_field} 散点图"
                        )
                    else:
                        st.info("散点图需要至少两个数值字段")
                        ch = None
                
                if ch is not None:
                    st.altair_chart(ch.interactive(), use_container_width=True)
            else:
                st.info("没有足够的数据进行可视化")
        except Exception as e:
            st.error(f"❌ 生成可视化图表失败：{str(e)}")
        
        # 数据对比模块
        st.subheader("⚖️ 数据对比")
        try:
            with st.spinner("正在准备数据对比..."):
                # 时间区间对比
                date_cols = [c for c, t in type_map.items() if t == "datetime"]
                if date_cols:
                    st.caption("时间区间对比")
                    compare_date_col = st.selectbox("选择日期字段", date_cols, key="compare_date_col")
                    
                    # 选择两个时间区间
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date1 = st.date_input("区间1开始日期", value=start_date, key="start_date1")
                        end_date1 = st.date_input("区间1结束日期", value=pd.to_datetime(start_date) + pd.Timedelta(days=7), key="end_date1")
                    with col2:
                        start_date2 = st.date_input("区间2开始日期", value=end_date - pd.Timedelta(days=7), key="start_date2")
                        end_date2 = st.date_input("区间2结束日期", value=end_date, key="end_date2")
                    
                    # 筛选两个区间的数据
                    df1 = filtered_df[
                        (pd.to_datetime(filtered_df[compare_date_col]).dt.strftime('%Y-%m-%d') >= start_date1.strftime('%Y-%m-%d')) &
                        (pd.to_datetime(filtered_df[compare_date_col]).dt.strftime('%Y-%m-%d') <= end_date1.strftime('%Y-%m-%d'))
                    ]
                    df2 = filtered_df[
                        (pd.to_datetime(filtered_df[compare_date_col]).dt.strftime('%Y-%m-%d') >= start_date2.strftime('%Y-%m-%d')) &
                        (pd.to_datetime(filtered_df[compare_date_col]).dt.strftime('%Y-%m-%d') <= end_date2.strftime('%Y-%m-%d'))
                    ]
                    
                    # 计算对比指标
                    if value_col:
                        val1 = df1[value_col].sum() if value_col in df1.columns else 0
                        val2 = df2[value_col].sum() if value_col in df2.columns else 0
                        diff = val2 - val1
                        diff_percent = (diff / val1 * 100) if val1 != 0 else 0
                        
                        st.info(f"区间1 {value_col}：{val1:.2f}")
                        st.info(f"区间2 {value_col}：{val2:.2f}")
                        st.info(f"变化量：{diff:.2f} ({diff_percent:.2f}%)")
                
                # 字段对比
                st.caption("字段对比")
                if len(nums_with_custom) >= 2:
                    field1 = st.selectbox("字段1", nums_with_custom, key="field1")
                    field2 = st.selectbox("字段2", nums_with_custom, index=1, key="field2")
                    
                    if field1 and field2:
                        # 计算相关性
                        correlation = filtered_df[[field1, field2]].corr().iloc[0, 1]
                        st.info(f"{field1} 与 {field2} 的相关系数：{correlation:.4f}")
                        
                        # 生成散点图
                        scatter_chart = alt.Chart(filtered_df).mark_circle(size=60).encode(
                            x=alt.X(field1, title=field1),
                            y=alt.Y(field2, title=field2),
                            tooltip=[field1, field2]
                        ).properties(
                            title=f"{field1} vs {field2}",
                            width=600,
                            height=400
                        ).interactive()
                        st.altair_chart(scatter_chart, use_container_width=True)
        except Exception as e:
            st.error(f"❌ 数据对比失败：{str(e)}")
        
        # 报表导出模块
        st.subheader("📤 报表导出")
        try:
            export_format = st.selectbox("导出格式", ["CSV", "Excel", "JSON", "HTML"])
            export_filename = st.text_input("导出文件名", value=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            if st.button("导出报表"):
                with st.spinner("正在导出报表..."):
                    # 准备导出数据
                    export_data = {
                        "原始数据": filtered_df,
                        "透视表结果": pv,
                        "tidy数据": tidy
                    }
                    
                    # 根据格式导出
                    if export_format == "CSV":
                        for name, data in export_data.items():
                            if not data.empty:
                                filepath = os.path.join(output_dir, f"{export_filename}_{name}.csv")
                                data.to_csv(filepath, index=False, encoding="utf-8-sig")
                        st.success(f"✅ 报表已导出到：{output_dir}")
                    elif export_format == "Excel":
                        filepath = os.path.join(output_dir, f"{export_filename}.xlsx")
                        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                            for name, data in export_data.items():
                                if not data.empty:
                                    data.to_excel(writer, sheet_name=name[:30], index=False)
                        st.success(f"✅ 报表已导出到：{filepath}")
                    elif export_format == "JSON":
                        filepath = os.path.join(output_dir, f"{export_filename}.json")
                        export_dict = {name: data.to_dict(orient="records") for name, data in export_data.items() if not data.empty}
                        import json
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(export_dict, f, ensure_ascii=False, indent=2)
                        st.success(f"✅ 报表已导出到：{filepath}")
                    elif export_format == "HTML":
                        filepath = os.path.join(output_dir, f"{export_filename}.html")
                        html_content = f"""
                        <html>
                        <head>
                            <title>数据分析报表</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                h1, h2 {{ color: #333; }}
                                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #f2f2f2; }}
                                .section {{ margin-bottom: 30px; }}
                            </style>
                        </head>
                        <body>
                            <h1>数据分析报表</h1>
                            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        """
                        for name, data in export_data.items():
                            if not data.empty:
                                html_content += f"<div class='section'><h2>{name}</h2>{data.to_html(index=False)}</div>"
                        html_content += "</body></html>"
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(html_content)
                        st.success(f"✅ 报表已导出到：{filepath}")
        except Exception as e:
            st.error(f"❌ 导出报表失败：{str(e)}")
        
        # 下载和保存部分
        st.subheader("💾 数据导出")
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                if 'pv' in locals() and not pv.empty:
                    csv = pv.to_csv(index=True).encode("utf-8-sig")
                    st.download_button(
                        label="📥 下载透视结果CSV",
                        data=csv,
                        file_name="pivot.csv",
                        mime="text/csv",
                        help="下载生成的透视表结果"
                    )
                else:
                    st.info("暂无透视结果可下载")
            except Exception as e:
                st.error(f"❌ 生成下载文件失败：{str(e)}")
        with c2:
            try:
                raw_csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 下载原始数据CSV",
                    data=raw_csv,
                    file_name="data.csv",
                    mime="text/csv",
                    help="下载原始数据"
                )
            except Exception as e:
                st.error(f"❌ 生成下载文件失败：{str(e)}")
        with c3:
            if save_local:
                try:
                    if 'pv' in locals() and not pv.empty:
                        pivot_path = save_to_local(pv, "pivot.csv", output_dir)
                        data_path = save_to_local(df, "data.csv", output_dir)
                        st.success(f"✅ 已保存到本地：\n- 透视结果：{pivot_path}\n- 原始数据：{data_path}")
                    else:
                        data_path = save_to_local(df, "data.csv", output_dir)
                        st.success(f"✅ 已保存到本地：\n- 原始数据：{data_path}")
                except Exception as e:
                    st.error(f"❌ 保存失败：{str(e)}")
            else:
                st.info("勾选'保存到本地'以保存结果到本地文件")