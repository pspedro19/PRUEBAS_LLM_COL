from apps.ai.models import AIConversation

print("\nVERIFICANDO TIPOS DE CAMPOS EN AIConversation:\n")

# Verificar pregunta_id
try:
    field = AIConversation._meta.get_field('pregunta_id')
    field_type = type(field).__name__
    print(f"Campo pregunta_id es de tipo: {field_type}")
    print(f"Es ForeignKey: {'SI' if 'ForeignKey' in field_type else 'NO'}")
except Exception as e:
    print(f"Error: {e}")

# Verificar todos los campos _id
print("\nTODOS LOS CAMPOS _id:")
for f in AIConversation._meta.get_fields():
    if '_id' in f.name:
        print(f"- {f.name}: {type(f).__name__}")