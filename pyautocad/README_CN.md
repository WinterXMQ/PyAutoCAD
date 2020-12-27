# `PyAutoCAD`'s API

## `Block`

`Block` 创建分为三步：
1. `Autocad`.`create_block`: 创建 `block`
2. `Autocad`.`add_entities`: 为创建的 `block` 添加 `Entity`
3. `Autocad`.`insert_block`: 将创建的 `block` 插入图形中
