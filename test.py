from model import Item

items = ["minecraft:stick", "minecraft:oak_planks", "daedalus_chunk_loader:chunk_loader_recipe"]
for item_name in items:
    item = Item(item_name)
    print(item.get_recipe())
    print(item.get_group())
    print("")