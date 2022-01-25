## BUSCOv5 - Benchmarking sets of Universal Single-Copy Orthologs.

Основные файлы буско и их описание.

Входной файл run_BUSCO.py настраивает логгер, парсит параметры и запускает пайплайн.

Он использует:

В init.py - загрузка основных модулей в общее простнарство имен.

Exception.py - просто заглушки ошибок.

BuscoLogger.py - декоратор логгер и сам логгер. Я выключил тут запись в файл, потому что это жутко раздрожало.

После парса параметров запускается BuscoConfigManager в который передаются параметры и настраивается файл конфигов (из параметров, из парамтеров баша, дефолтный в виде окружения).

После этого создаеттся BuscoMaster, передаются ему параметры и запускется run().

На первом шаге опять запускается BuscoConfigManager. В нем создается BuscoConfigMain, который конфигурируется и валидируется. 

После этого запускается harmonize_auto_lineage_settings. Настраивается задачка на запуск и запускается. Ну и плюс обработка ошибок. В самом конце независимо от результата запускается AnalysisRunner.move_log_file(self.config).

Запуск раннер в двух режимах:

BatchRunner(self.config_manager) и SingleRunner(self.config_manager) в зависимости от флага batch_mode в конфига (пока не понятно как он ставится).
 
С конфигами они адски намудрили.

Базовые параметры:

```
DEFAULT_ARGS_VALUES = {
        "out_path": os.getcwd(),
        "cpu": 1,
        "force": False,
        "restart": False,
        "quiet": False,
        "download_path": os.path.join(os.getcwd(), "busco_downloads"),
        "datasets_version": "odb10",
        "offline": False,
        "download_base_url": "https://busco-data.ezlab.org/v5/data/",
        "auto-lineage": False,
        "auto-lineage-prok": False,
        "auto-lineage-euk": False,
        "update-data": False,
        "evalue": 1e-3,
        "limit": 3,
        "use_augustus": False,
        "long": False,
        "batch_mode": False,
        "tar": False,
}

DEPENDENCY_SECTIONS = {
    "tblastn",
    "makeblastdb",
    "prodigal",
    "sepp",
    "metaeuk",
    "augustus",
    "etraining",
    "gff2gbSmallDNA.pl",
    "new_species.pl",
    "optimize_augustus.pl",
    "hmmsearch",
}
```

TODO: Описать как устроена обработка ошибок

Есть BaseConfig(ConfigParser) потом есть PseudoConfig(BaseConfig) потом есть BuscoConfig(ConfigParser, metaclass=ABCMeta) и еще BuscoConfigAuto(BuscoConfig) 
и еще BuscoConfigMain(BuscoConfig, BaseConfig). У кого-то классы головного мозга случились.

Я чуть посокращал конфиг, как логика устроена:

- засовываем все параметры в библиотечный configparser и прописываем дефолтные значения, потом добавляем из конфг файла значение и из параметров
- потому проверка указали ли прокариот или эукариот как линэйдж, ну тут она реально не к месту (тут это под соусом _check_value_constraints)
- проверяем что есть все обязательные параметры
- проверяем что в аутпут пути нет слешей
- что параметр limit между 0 и 20 (check_limit_value). Это сколько он кандидатов рассматривает, по дефолту это 3. Для аннотации генов это должно быть значительно больше!!! Я границы поставил 0 200 и дефолтное 20.
- предупредить о странным evalue (check_evalue). Дефолтное 1e-3.
- expand_all_paths ну понятно но это не чек
- проверка следов предыдущего запуска check_no_previous_run, если force то папку будет удалена, если реран то перезапущена или буско убит
- после этого check_allowed_keys - похоже проверка того что уже было проверена ранее, возможно можно убрать
- создание папки аутпута и проверка существования инпута check_required_input_exists
- check_batch_mode проверяет папка или файл на входе если папка то включает батч мод
- init_downloader иницилизирует BuscoDownloadManager 
- и финально log_config вывести в красивом виде настройки

### Инициация BuscoDownloadManager

Он управляется параметрами offline update-data download_base_url download_path


Как оно работает

- создает папку для скачивания баз данных create_main_download_dir
- скачивает versions_file с буско file_versions.tsv, это информация о таксон специфичных моделях буско

### harmonize_auto_lineage_settings

- запускается config.check_lineage_present() и проверяется указал ли пользователь lineage, параметры lineage_dataset и datasets_version, в целом все сводится к проверке что это odb10 база данных по ее имени только
- если на предыдущем шаге проверка не пройдена, то запускается автоподбор подходящей базы данных, то есть ставится флаг auto-lineage 
- оно управляется флагами auto-lineage-prok auto-lineage-euk auto-lineage

### После этого запускается BatchRunner или SingleRunner и в нем runner.run()

На первом этапе происходит выбор lineage get_lineage().

Если auto-lineage то оно начинает пытатся определать вызывая self.auto_select_lineage() в результате будет установлен lineage_dataset и parent_dataset (если не вирусы)

### Логика выбора датасата AutoSelectLineage

В зависимости от флагов выбирается из про эу и археи. Передаются все конфиги в класс, ну как везде в буско внутрях, конфиги хранят стейт.

Потому запускается asl.run_auto_selector()

```python
@log("No lineage specified. Running lineage auto selector.\n", logger)
def auto_select_lineage(self):
    from busco.AutoLineage import (
        AutoSelectLineage,
    )  # Import statement inside method to avoid circular imports

    asl = AutoSelectLineage(self.config_manager)
    asl.run_auto_selector()
    asl.get_lineage_dataset()
    asl.set_best_match_lineage()
    lineage_dataset = asl.best_match_lineage_dataset
    runner = asl.selected_runner
    type(self).all_runners.extend(asl.runners)
    asl.reset()
    return lineage_dataset, runner
```

После этого запускается run_lineages_list(list), внутри которого для каждого линейджа:
- создается автоконфиг self.config_manager.load_busco_config_auto(self.current_lineage)
-- в котором создается директория для запуска
-- создается копия настроек общих и сслыка на downloading manager
-- скачивается и распакаковывается и проверяется по md5 датасет линэйджа












