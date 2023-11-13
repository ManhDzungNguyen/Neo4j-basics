# Neo4j Data Migration

## Chú ý khi muốn migrate data sang server mới
Việc migrate DB từ v3.4.5 lên v5.11.0 rất phức tạp, không thể migrate lên ngay được mà phải qua từng major version của Neo4j, tham khảo: [Migrating/Upgrading from Neo4j 3.5.20 to 5.9.0](https://community.neo4j.com/t/migrating-upgrading-from-neo4j-3-5-20-to-5-9-0/63171). Migrate mỗi version đều rất phức tạp nên không suggest theo cách này.

### Chú ý khi export data ở server cũ

- Đừng dùng [dump and load commands](https://neo4j.com/docs/operations-manual/current/kubernetes/operations/dump-load/) của Neo4j. Version và format dump file của Neo4j 3.4.5 và 5.11.0 khác hẳn nhau nên Neo4j v5.11.0 không thể load được dump file từ Neo4j v3.4.5. Bên cạnh đó lệnh `neo4j-admin database load` khi thử nghiệm ở server chỉ chạy được với quyền `sudo` và lệnh này sẽ thay đổi quyền của một vài directory của Neo4j, khiến cho DB không thể khởi động được, có thể phải cài lại Neo4j. [neo4j don't start after load a .dump file](https://stackoverflow.com/questions/46179387/neo4j-dont-start-after-load-a-dump-file)

- Đừng dùng query [apoc.export.json.all](https://neo4j.com/docs/apoc/current/overview/apoc.export/apoc.export.json.all/) để export toàn bộ data của database cũ vì nếu DB quá lớn thì việc export sẽ bị chết giữa chừng do server tự ngắt.

- Hãy dùng query [apoc.export.json.query](https://neo4j.com/docs/apoc/current/overview/apoc.export/apoc.export.json.query/) với query export tầm 50k record mỗi file và tách thành export node và relationship riêng.

### Chú ý khi import data ở server mới
- Đừng dùng query [apoc.import.json](https://neo4j.com/docs/apoc/current/overview/apoc.import/apoc.import.json/) để import data sau khi export từ DB cũ sang DB mới. File json export được ra bản cũ có schema khác với schema file để import vào bản mới. Bên cạnh đó, kể cả sửa lại file này cho chuẩn format của bản mới thì việc import cũng sẽ dễ bị dính lỗi CONSTRAIN rất khó sửa, khiến cho Neo4j DB không thể khởi động lại và có thể phải cài lại. 

- Hãy convert các file json export ra về các file json với định dạng `{"data":[...]}` và dùng query [apoc.load.json](https://neo4j.com/docs/apoc/current/overview/apoc.load/apoc.load.json/) để load node, rels theo định dạng mình muốn.


## Các bước để chuyển dữ liệu 1 sự kiện từ Neo4j v3.4.5 sang DB v5.11.0
- Old_server: 10.9.3.178
- New_server: 10.9.3.209
- Các file python chạy ở server `10.9.3.209` với `venv`: `/home/dungnguyen/work/neo4j/venv`

### 1. Export nodes and relationships data from Neo4j DB v3.4.5 based on their labels
1. thêm `apoc.export.file.enabled=true` và `dbms.security.procedures.whitelist=apoc.*` vào file `/etc/neo4j/neo4j.conf` ở server cũ để cho phép plugin APOC export data.\

2. run `1_neo_3.4_export_data.py`, thay đổi label và số lượng node, relationship cho phù hợp trong code (nên chạy ở server mới vì server cũ không có python3). Code này sẽ export tất cả node và rel data của 1 sự kiện vào folder /tmp (Neo4j 3.4.5 khi thử nghiệm chỉ cho export vào folder này).

### 2. chuyển data từ server cũ sang server mới:
1. ở server 10.9.3.178 move tất cả các file node và relationship vào thư mục mới:
    - nodes: `mv /tmp/all_person_data_* /home/tungnguyen/dungnguyen/neo4j/person_data/`
    - rels: `mv /tmp/all_mutual_6586_* /home/tungnguyen/dungnguyen/neo4j/mutual_6586/`

2. chuyển tất cả các file này sang server mới:
    - (server mới): `scp -r tungnguyen@10.9.3.178:/home/tungnguyen/dungnguyen/neo4j /home/dungnguyen/work/neo4j/archive/`

### 3. import data vào database mới:
1. chuyển đổi định dạng file json nodes và rels về định dạng để import được vào database mới với apoc.load.json:
    - Chú ý thay đổi path, label, số lượng nodes và rels trong code cho phù hợp
    - run `2_convert_neo_3_4_node_export_files_to_import_files.py`
    - run `3_convert_neo_3_4_rel_export_files_to_import_files.py`

2. đẩy dữ liệu sau khi format vào database mới:
    - run `4_neo_5_11_load_data.py`, thay đổi path, label và số lượng node, relationship cho phù hợp trong code
                                                                        
                                                                