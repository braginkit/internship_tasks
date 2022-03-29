import dask.dataframe as dd
import pandas as pd
from dask.diagnostics import ProgressBar
import time

# это я использовал для отслеживания прогресса вычислений и треккинга общего времени
ProgressBar().register()
start = time.time()

# черех pandas читать очень долго (у меня больше 100 секунд), через dask в 200 раз быстрее (меньше 1 секунды)
data = dd.read_csv('pp-complete.csv', header=None, dtype={
    0: 'str', 1: 'int', 2: 'str', 3: 'str', 4: 'str', 5: 'str', 6: 'str', 7: 'str',
    8: 'str', 9: 'str', 10: 'str', 11: 'str', 12: 'str', 13: 'str', 14: 'str', 15: 'str'
    })

# дропаем лишние данные
dask_data = data.drop(columns=[1, 2, 3, 4, 5, 6, 14, 15])

# проиндексируем по уникальному ключу перед переводом в pandas
dask_data_new = dask_data.set_index(0)

# также разобьем данные на 46 секций перед переводом в pandas
# (на 46, потому что 4,56 Гб должны быть разбиты примерно по 100 Мб на секцию для большей эффективности dask)
dask_data_repartitioned = dask_data_new.repartition(npartitions=46)

# дальше, наверно, упрощать никак, так что переходим к pandas
pandas_data = dask_data_repartitioned.compute()

# теперь найдем индексы той недвижимости, что встречается несколько раз
pandas_filter = pandas_data[pandas_data.duplicated(subset=[7, 8, 9, 10, 11, 12, 13], keep=False)]
pandas_filter = pandas_filter.drop_duplicates(subset=[7, 8, 9, 10, 11, 12, 13])
list_of_keys = pandas_filter.index.values.tolist()
print(type(list_of_keys[0]))
print(list_of_keys[0])

# выберем все данные о недвижимости, которая встречается больше одного раза, воспользовавшись сформированным списком ключей
# здесь можно было бы использовать .iloc, если бы ключи были целочисленные, но ключи строковые, так что придется использовать .loc
pandas_data = pandas_data.loc[list_of_keys, :]
pandas_data.to_csv(path_or_buf='pp-result.csv')
end = time.time()
print('Общее время работы программы: ', end - start)
