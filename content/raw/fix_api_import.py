f='/opt/ant2-proxy/web/src/pages/IpJail.jsx'
t=open(f).read().replace("from '../api'","from '../api/client'")
open(f,'w').write(t)
print('fixed:', open(f).read().count("api/client"))
