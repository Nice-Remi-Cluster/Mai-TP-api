# TODO
- [ ] 完善水鱼api的返回模型
  - [ ] v1/divingfish/health
  - [ ] v1/divingfish/music_data
  - [ ] v1/divingfish/chart_stats_update
  - [ ] v1/divingfish/get_user_b_scores


### api对外开放

已实现api localhost:8080/docs

水鱼

- [x] 官方api水鱼存活检测
- [ ] 自实现水鱼存活检测
- [x] 更新同步水鱼方maimai歌曲数据
- [x] 获取歌曲封面图片
- [x] 通过qq或水鱼用户名获取用户的b50, b40
- [x] 获取铺面拟合难度等数据
- [x] 获取单曲信息
- [x] 获取单曲额外信息如拟合难度等
- [x] 获取铺面难度统计信息
- [ ] 更新用户成绩信息
- [ ] 更新用户单曲成绩
- [ ] 清除所有maimai成绩

落雪

> 待申请成为开发者

divingfish

- [ ] 待制作待办事项


## 需要对接或者实现的api

### 水鱼官方api

- [x] /alive_check
- [x] /music_data 获取 maimai 的歌曲数据
- [x] */covers 按 ID 获取歌曲的封面图片
- [x] /query/player 获取用户的简略成绩信息
- [x] /chart_stats 返回谱面的拟合难度等数据

以下需要Import-token
- [ ] /player/update_records 更新用户的成绩信息
- [ ] /player/update_record 更新用户的单曲成绩
- [ ] /player/delete_records 清除用户的所有 maimai 成绩信息


### 水鱼辅助api
- [ ] 水鱼服务检查


### 落雪api

> 待申请成为开发者

### dxrating

- [ ] 待制作待办事项