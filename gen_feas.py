import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler
from numpy import random

random.seed(2019)
train = pd.read_csv("new_data/train.csv")
train_target = pd.read_csv('new_data/train_target.csv')
train = train.merge(train_target, on='id')
test = pd.read_csv("new_data/test.csv")

df = pd.concat([train, test], sort=False, axis=0)
# 特征工程
df['missing'] = (df == -1).sum(axis=1).astype(float)  # 统计每行中为-999的个数
df['bankCard'] = df['bankCard'].fillna(value=0)  # bankCard存在空值
# 删除重复列
duplicated_features = ['x_0', 'x_1', 'x_2', 'x_3', 'x_4', 'x_5', 'x_6',
                       'x_7', 'x_8', 'x_9', 'x_10', 'x_11', 'x_13',
                       'x_15', 'x_17', 'x_18', 'x_19', 'x_21',
                       'x_23', 'x_24', 'x_36', 'x_37', 'x_38', 'x_57', 'x_58',
                       'x_59', 'x_60', 'x_77', 'x_78'] + \
                      ['x_22', 'x_40', 'x_70'] + \
                      ['x_41'] + \
                      ['x_43'] + \
                      ['x_45'] + \
                      ['x_61']
# 类别组合特征
count = 0
for c in duplicated_features:
    if count == 0:
        df['new_ind' + str(-1)] = df[c].astype(str) + '_'
        count += 1
    else:
        df['new_ind' + str(-1)] += df[c].astype(str) + '_'
for c in ['new_ind' + str(-1)]:
    d = df[c].value_counts().to_dict()
    df['%s_count' % c] = df[c].apply(lambda x: d.get(x, 0))
df.drop(columns=['new_ind' + str(-1)], inplace=True)

df = df.drop(columns=duplicated_features)
print(df.shape)

no_features = ['id', 'target'] + ['bankCard', 'residentAddr', 'certId', 'dist', 'new_ind1', 'new_ind2']
features = []
numerical_features = ['lmt', 'certValidBegin', 'certValidStop', 'missing']  # 不是严格意义的数值特征，可以当做类别特征
categorical_features = [fea for fea in df.columns if fea not in numerical_features + no_features]

group_features1 = [c for c in categorical_features if 'x_' in c]  # 匿名
group_features2 = ['bankCard', 'residentAddr', 'certId', 'dist']  # 地区特征
group_features3 = ['lmt', 'certValidBegin', 'certValidStop']  # 征信1

group_features4 = ['age', 'job', 'ethnic', 'basicLevel', 'linkRela']  # 基本属性
group_features5 = ['ncloseCreditCard', 'unpayIndvLoan', 'unpayOtherLoan', 'unpayNormalLoan', '5yearBadloan']

group_features = [
    group_features1, group_features2, group_features3, group_features4,
    group_features5,
]

for index, ind_features in enumerate(group_features):
    index += 1
    count = 0
    for c in ind_features:
        if count == 0:
            df['new_ind' + str(index)] = df[c].astype(str) + '_'
            count += 1
        else:
            df['new_ind' + str(index)] += df[c].astype(str) + '_'
    for c in ['new_ind' + str(index)]:
        d = df[c].value_counts().to_dict()
        df['%s_count' % c] = df[c].apply(lambda x: d.get(x, 0))
    df.drop(columns=['new_ind' + str(index)], inplace=True)

from sklearn.preprocessing import LabelEncoder


def create_group_fea(df_, groups_fea, group_name):
    count = 0
    for c in groups_fea:
        if count == 0:
            df_[group_name] = df_[c].astype(str) + '_'
            count += 1
        else:
            df_[group_name] += df_[c].astype(str) + '_'
    for c in [group_name]:
        tmp_d = df_[c].value_counts().to_dict()
        df_['%s_count' % c] = df_[c].apply(lambda x: tmp_d.get(x, 0))
    lb = LabelEncoder()
    df_[group_name] = lb.fit_transform(df_[group_name])
    # df_.drop(columns=[group_name], inplace=True)
    return df_


# certId
df['certId_first2'] = df['certId'].apply(lambda x: int(str(x)[:2]))  # 前两位
df['certId_middle2'] = df['certId'].apply(lambda x: int(str(x)[2:4]))  # 中间两位
df['certId_last2'] = df['certId'].apply(lambda x: int(str(x)[4:6]))  # 最后两位

# 组合特征
certId_first2_loanProduct = ['certId_first2', 'loanProduct']
df = create_group_fea(df, certId_first2_loanProduct, 'certId_first2_loanProduct')
certId_middle2_loanProduct = ['certId_middle2', 'loanProduct']
df = create_group_fea(df, certId_middle2_loanProduct, 'certId_middle2_loanProduct')
certId_last2_loanProduct = ['certId_last2', 'loanProduct']
df = create_group_fea(df, certId_last2_loanProduct, 'certId_last2_loanProduct')

df['lmt_bin'] = pd.qcut(df['certValidBegin'], 20, labels=[i for i in range(20)])
certId_first2_lmt = ['certId_first2', 'lmt_bin']
df = create_group_fea(df, certId_first2_lmt, 'certId_first2_lmt')
certId_middle2_lmt = ['certId_middle2', 'lmt_bin']
df = create_group_fea(df, certId_middle2_lmt, 'certId_middle2_lmt')
certId_last2_lmt = ['certId_last2', 'lmt_bin']
df = create_group_fea(df, certId_last2_lmt, 'certId_last2_lmt')

certId_first2_basicLevel = ['certId_first2', 'basicLevel']
df = create_group_fea(df, certId_first2_basicLevel, 'certId_first2_basicLevel')
certId_middle2_basicLevel = ['certId_middle2', 'basicLevel']
df = create_group_fea(df, certId_middle2_basicLevel, 'certId_middle2_basicLevel')
certId_last2_basicLevel = ['certId_last2', 'basicLevel']
df = create_group_fea(df, certId_last2_basicLevel, 'certId_last2_basicLevel')

# dist
df['dist_first2'] = df['dist'].apply(lambda x: int(str(x)[:2]))  # 前两位
df['dist_middle2'] = df['dist'].apply(lambda x: int(str(x)[2:4]))  # 中间两位
df['dist_last2'] = df['dist'].apply(lambda x: int(str(x)[4:6]))  # 最后两位

dist_first2_loanProduct = ['dist_first2', 'loanProduct']
df = create_group_fea(df, dist_first2_loanProduct, 'dist_first2_loanProduct')
dist_middle2_loanProduct = ['dist_middle2', 'loanProduct']
df = create_group_fea(df, dist_middle2_loanProduct, 'dist_middle2_loanProduct')
dist_last2_loanProduct = ['dist_last2', 'loanProduct']
df = create_group_fea(df, dist_last2_loanProduct, 'dist_last2_loanProduct')

# residentAddr
df['residentAddr_first2'] = df['residentAddr'].apply(lambda x: int(str(x)[:2]) if x != -999 else -999)  # 前两位
df['residentAddr_middle2'] = df['residentAddr'].apply(lambda x: int(str(x)[2:4]) if x != -999 else -999)  # 中间两位
df['residentAddr_last2'] = df['residentAddr'].apply(lambda x: int(str(x)[4:6]) if x != -999 else -999)  # 最后两位

residentAddr_first2_loanProduct = ['residentAddr_first2', 'loanProduct']
df = create_group_fea(df, residentAddr_first2_loanProduct, 'residentAddr_first2_loanProduct')
residentAddr_middle2_loanProduct = ['residentAddr_middle2', 'loanProduct']
df = create_group_fea(df, residentAddr_middle2_loanProduct, 'residentAddr_middle2_loanProduct')
residentAddr_last2_loanProduct = ['residentAddr_last2', 'loanProduct']
df = create_group_fea(df, residentAddr_last2_loanProduct, 'residentAddr_last2_loanProduct')

# 数值特征处理
df['certValidPeriod'] = df['certValidStop'] - df['certValidBegin']
# 类别特征处理

# 特殊处理
# bankCard 5991
# residentAddr 5288
# certId 4033
# dist 3738
cols = ['bankCard', 'residentAddr', 'certId', 'dist']
# 计数
for col in cols:
    df['{}_count'.format(col)] = df.groupby(col)['id'].transform('count')

# 对lmt进行mean encoding
for fea in tqdm(cols):
    grouped_df = df.groupby(fea).agg({'lmt': ['mean', 'median']})
    grouped_df.columns = [fea + '_' + '_'.join(col).strip() for col in grouped_df.columns.values]
    grouped_df = grouped_df.reset_index()
    # print(grouped_df)
    df = pd.merge(df, grouped_df, on=fea, how='left')
df = df.drop(columns=cols)  # 删除四列

for fea in tqdm(['certId_first2', 'certId_middle2', 'certId_last2']):
    grouped_df = df.groupby(fea).agg({'lmt': ['mean', 'median']})
    grouped_df.columns = [fea + '_' + '_'.join(col).strip() for col in grouped_df.columns.values]
    grouped_df = grouped_df.reset_index()
    # print(grouped_df)
    df = pd.merge(df, grouped_df, on=fea, how='left')

for fea in tqdm(['certId_first2_loanProduct', 'certId_first2_basicLevel']):
    grouped_df = df.groupby(fea).agg({'lmt': ['mean', 'median']})
    grouped_df.columns = [fea + '_' + '_'.join(col).strip() for col in grouped_df.columns.values]
    grouped_df = grouped_df.reset_index()
    # print(grouped_df)
    df = pd.merge(df, grouped_df, on=fea, how='left')

for fea in tqdm(['dist_first2', 'dist_middle2', 'dist_last2']):
    grouped_df = df.groupby(fea).agg({'lmt': ['mean']})
    grouped_df.columns = [fea + '_' + '_'.join(col).strip() for col in grouped_df.columns.values]
    grouped_df = grouped_df.reset_index()
    df = pd.merge(df, grouped_df, on=fea, how='left')


# dummies
df = pd.get_dummies(df, columns=categorical_features)
df.head().to_csv('tmp/df.csv', index=None)
print("df.shape:", df.shape)

features = [fea for fea in df.columns if fea not in no_features]
train, test = df[:len(train)], df[len(train):]


def load_data():
    return train, test, no_features, features
