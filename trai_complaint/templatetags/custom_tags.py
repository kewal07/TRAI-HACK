from django import template

register = template.Library()

@register.filter(name='get_color')
def get_color(v1):
	# print(v1)
	colors = ['bg-aqua','bg-yellow','bg-green']
	ret = colors[(v1-1)%3]
	return ret

@register.filter(name='replace_space')
def replace_space(v1):
	# print(v1)
	ret = v1.replace(" ","_")
	return ret

@register.filter(name='get_status_state')
def get_status_state(v1):
	# print(v1)
	ret = "label-succes"
	if v1 == 'O':
		ret = 'label-warning'
	elif v1 == 'RO':
		ret = 'label-danger'
	return ret
