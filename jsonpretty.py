import  json
o = open('ler.json', 'r')
a = json.load(o)
o.close()
out = open('ler2.json', 'w')
out.write(json.dumps(a, indent=4, sort_keys=True))
out.close()