from flask import Flask, render_template, request, redirect
import sqlite3, os
from flask import send_file


app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html", link=get_link()+"uploader")


def get_link():
	return "https://serveur1gratuit.pythonanywhere.com/"


@app.route('/recherche', methods=['POST'])
def rechercher():
	nom=request.form['sherch']
	return redirect('/'+nom)


def ch_name():
	lst=open("dernier_nom.txt")
	t=lst.read()
	t=t[7:len(t)]
	nom="fichier"+str(int(t)+1)
	lst=open("dernier_nom.txt", "w")
	lst.write(nom)
	lst.close()
	return nom


@app.route('/suprimme/<nom>')
def supprimer_site(nom):
	connector=sqlite3.connect(os.getcwd()+"/db.sqlite3")
	curseur=connector.cursor()
	domaine=get_site(nom)
	curseur.execute('delete from sites WHERE (nom)=(?)', (nom,))
	connector.commit()
	os.remove("/home/serveur1gratuit/mysite/server/templates/"+domaine)
	return "<center><h1>"+nom +" a été supprimé</h1></center>"+extension_home()




def get_site(nom):
	connector=sqlite3.connect(os.getcwd()+"/db.sqlite3")
	curseur=connector.cursor()
	t=curseur.execute('SELECT domaine FROM sites WHERE nom=?', (nom,)).fetchone()
	try:
		return "".join(t)
	except:
		return False

def extension_telecharger(domaine):
	return '<br><a href="'+get_link()+'/telecharge/'+domaine+'"> Télécharger</a><br>'

def extention_supprimmer(nom):
	return '<br><a href="'+get_link()+'/suprimme/'+nom+'">Supprimer</a><br><br>'

def extension_home():
	return '<br><a href="'+get_link()+'">Retour</a><br>'

def extension_poid(domaine):
	return str(os.path.getsize("/home/serveur1gratuit/mysite/server/templates/"+domaine)/1000000)+" MB"


@app.route('/<nom>')
def appf(nom):
	site=get_site(nom)
	if not site:
		return "<h1>Fichier "+nom+" inexistant "+extension_home()+"</h1>"
	comp=site.split('.')
	ext="<h2> Format : "+comp[1]+"</h2><br>"+"Poids : "+extension_poid(site)+"<br>"
	image_ext=["jpg", "png", "jpeg"]
	if comp[1]!='html':
		if comp[1] in image_ext:
			return extension_telecharger(nom)+ext+extention_supprimmer(nom)+'<img src="https://www.pythonanywhere.com/user/serveur1gratuit/files/home/serveur1gratuit/mysite/server/templates/'+site+'">'
		else:
			try:
				return extension_telecharger(nom)+ext+extention_supprimmer(nom)+'<pre class="brush: "'+comp[1]+'>'+render_template(site)+"</pre>"
			except:
				return "Affichage impossible "+extention_supprimmer(nom)+extension_telecharger(nom)+ext
	else:
		return extension_telecharger(nom)+ext+extention_supprimmer(nom)+render_template(site)



@app.route('/telecharge/<domaine>')
def plot_csv(domaine):
	domaine=get_site(domaine)
	return send_file("/home/serveur1gratuit/mysite/server/templates/"+domaine ,attachment_filename=domaine,as_attachment=True)



def exist(domaine, nom):
	connector=sqlite3.connect(os.getcwd()+"/db.sqlite3")
	curseur=connector.cursor()

	#curseur.execute('CREATE table sites (domaine, nom)')
	#connector.commit()

	t=curseur.execute('SELECT domaine, nom FROM sites').fetchall()
	print(t)
	dm=(domaine.split('.')[0], nom, )
	for i in t:
		if dm[0] in i[0] or dm[1]==i[1]:
			return False
	return True



def saver(domaine, nom):
	connector=sqlite3.connect(os.getcwd()+"/db.sqlite3")
	curseur=connector.cursor()
	curseur.execute('INSERT into sites (domaine, nom) values (?, ?)', (domaine, nom, ))
	connector.commit()
	return




@app.route('/uploader', methods = ['GET', 'POST'])
def upload_fileg():
	if request.method == 'POST':
		try:
			f=request.files['file']
			nom=request.form['nom']
		except:
			return redirect('/')
		if nom=='' or f.filename=='':
			return redirect('/')
		dmn=f.filename.split('.')
		dmn=nom+"."+dmn[len(dmn)-1]
		if exist(dmn, nom):
			saver(dmn, nom)
			try:
				f.save(os.path.join("/home/serveur1gratuit/mysite/server/templates/", dmn))
			except:
				return "<h1>Il n'y a plus de place dans le serveur. Réssayer</h1>"
			return render_template('uploaded_site.html', domaine=dmn,nom_site=nom, lien=get_link()+nom)
		else:
			return "<h1>Le nom est déja utilisé.</h1>"+extension_home()

if __name__ == '__main__':
   app.run(debug = True)

