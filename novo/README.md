## Gramática nova
PROGRAM → DEV_SEC CMD_SEC
DEV_SEC → dispositivos : DEV_LIST fimdispositivos
DEV_LIST → DEV_ITEM | DEV_LIST DEV_ITEM
DEV_ITEM → ID_DEV | ID_DEV [ ID_OBS ]
CMD_SEC → CMD_LIST
CMD_LIST → CMD ; | CMD_LIST CMD ;
CMD → ATTR | OBSACT | ACT
ATTR → def ID_OBS = VAL
OBSACT → quando OBS : ACT | quando OBS : ACT senao ACT
OBS → SIMPLE_OBS | SIMPLE_OBS AND OBS
SIMPLE_OBS → ID_OBS OP_LOGIC VAL
VAL → NUM | BOOL
ACT → execute ACTION em ID_DEV | alerta para ID_DEV : MSG | difundir : MSG -> [ DEV_LIST_N ] | difundir : MSG ID_OBS -> [ DEV_LIST_N ]
ACTION → ligar | desligar
DEV_LIST_N → ID_DEV | ID_DEV , DEV_LIST_N