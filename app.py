import os
from flask import Flask,render_template,session,redirect,url_for,request,flash,jsonify,send_from_directory
from models import db,User,Docs
from forms import SignupForm,SigninForm
from werkzeug import secure_filename
import flask.ext.whooshalchemy

app=Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #for sessions

ROOT_FOLDER='/'
UPLOAD_FOLDER = 'uploads/'
IMAGE_FOLDER='thumbnail_bucket'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sairam@localhost/ita' 

app.config['ROOT_FOLDER']=ROOT_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER   # defining the upload folder
app.config['IMAGE_FOLDER']=IMAGE_FOLDER
app.config['WHOOSH_BASE'] = 'path/to/whoosh/base'

db.init_app(app)

@app.route('/')
def index():
	return render_template('landing.html')
	
@app.route('/hello')
def hello():
	return "Hello World!"
	
@app.route('/login',methods=['GET','POST'])
def login():
	form=SigninForm()

	if request.method=='POST': #do the login
		if form.validate()==False:
			return render_template('login.html',form=form)
		else:
			session['email']=form.email.data
			return redirect('/s1')			
	else: #show login form
		return render_template('login.html',form=form)

@app.route('/home')
def home():
    return render_template('main.html') 

@app.route('/page')
def page():
    return render_template('dirPagination.tpl.html')           
	
@app.route('/logout')
def logout():
	session.pop('email',None)
	# flash('You have successfully logged out')
	return redirect(url_for('index'))

@app.route('/signup',methods=['GET','POST'])																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																															
def signup():
	form=SignupForm()

	if request.method=='POST':
		if form.validate() ==False:
			return render_template('signup.html',form=form)
		else:
			newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
			db.session.add(newuser)
			db.session.commit()
			# redirect(url_for('login'))
			return jsonify({'status':201,'firstname':newuser.firstname,'lastname':newuser.lastname,'username':newuser.email,'message':"User successfully created"}),201,{'Location':url_for('login')} #location : url for new created user                
			
	elif request.method=='GET':
		return render_template('signup.html',form=form)	

# @app.route('/signup1',methods=['GET','POST'])
# def sup():
#     if request.method=='POST':
#         if request.json:
#             json=request.json
#             print json
#             return jsonify(json)
#         else:
#             print "no json"    


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
    	resp={}
        file = request.files['file']
        docname=request.form['docname']
        author=request.form['author']
        publisher=request.form['publisher']
        tags=request.form['tags']
        img=request.files['img']    

        if not file:
        	resp['status']=500
        	resp['message']='Internal Server Error'
        	return jsonify(resp)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            size=os.stat(path).st_size
            img_path=os.path.join(app.config['IMAGE_FOLDER'], img.filename)
            img.save(img_path)

            
            #save in database

            doc=Docs(docname,filename,author,publisher,tags,size,path,img.filename)	
            db.session.add(doc)
            db.session.flush()
            did=doc.docid
            db.session.commit()




            #generating response
            resp['status']=200
            resp['file_name']=filename
            resp['id']=did
            resp['message']='file uploaded successfully'
        #    return redirect(url_for('uploaded_file',filename=filename))
            return jsonify(resp)
        else:
        	resp['status']=415
        	resp['message']='file type not supported'
        	return jsonify(resp)    
    return render_template('upload.html')

@app.route('/upload_image/<int:id>',methods=['POST'])
def upload_image(id):
    resp={}
    file = request.files['img']

    if not file:
        resp['status']=500
        resp['message']='Internal Server Error'
        return jsonify(resp)
    else:
        path=os.path.join(app.config['IMAGE_FOLDER'], file.filename)
        file.save(path)
        #update in database
        doc=Docs.query.get(id)
        doc.imgpath=file.filename
        db.session.commit()

        resp["status"]=200
        resp["message"]="image added successfully"
        resp["image_path"]=path

        return jsonify(resp)    



    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename) 

@app.route('/image/<filename>')
def view_image(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'],filename) 

@app.route('/delete/<int:id>')
def delete(id):
    resp={}
    doc=Docs.query.get(id)
    db.session.delete(doc)
    db.session.commit()
    resp["id"]=200
    resp["message"]="resource deleted successfully"
    return jsonify(resp)

@app.route('/update/<int:id>',methods=['POST','GET'])
def update(id):
    if request.method=='POST':
        resp={}
        #get all data
        file = request.files['file']
        docname=request.form['docname']
        author=request.form['author']
        publisher=request.form['publisher']
        tags=request.form['tags']
        path=os.path.join(app.config['UPLOAD_FOLDER'], docname)
        file.save(path)
        size=os.stat(path).st_size
        
        #update database 
        doc=Docs.query.get(id)
        #db.session.delete(doc)

        doc.docname=docname
        doc.author=author
        doc.publisher=publisher
        doc.tags=tags
        doc.docsize=size
        doc.docpath=path

        db.session.commit()

        #generate response 
        resp["staus"]=200
        resp["message"]="updated successfully"
        return jsonify(resp)
    else:
        d=Docs.query.get(id)
        return render_template('modify.html',data=d)    




@app.route('/docs')
def display():
    resp={}
    docs=Docs.query.all()
    resp['data']=[]
    for doc in docs:
        resp['data'].append({'id':doc.docid,'name':doc.docname,'filename':doc.filename,'author':doc.author,'publisher':doc.publisher,'tags':doc.tags,'size':doc.docsize,'url':doc.docpath,'image':doc.imgpath})
    return jsonify(resp)

@app.route('/doc/<int:id>')
def doc(id):
    resp={}
    
    d=Docs.query.get(id)

    if not d:
        resp["message"]="Doc not found"
        resp["status"]=404
    else:
        resp["data"]=[]
        resp["status"]=200
        resp['data'].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'tags':d.tags,'size':d.docsize,'url':d.docpath,'image':d.imgpath})

    return jsonify(resp)    
            

@app.route('/s',methods=['POST'])
def s():
    jsonData=request.get_json(force=True)
    fil=jsonData['filter']
    name=jsonData['name']

    

    if fil=='docname':
        doc=Docs.query.filter(Docs.docname.like("%"+name+"%")).all()
    elif fil=='author':
        doc=Docs.query.filter(Docs.author.like("%"+name+"%")).all()
    elif fil=='publisher':
        doc=Docs.query.filter(Docs.publisher.like("%"+name+"%")).all()
    elif fil=='tags':
        doc=Docs.query.filter(Docs.tags.like("%"+name+"%")).all()
    elif fil=='year':
        doc=Docs.query.filter(Docs.uploaded.like("%"+name+"%")).all()        

    resp={}
   # doc=Documents.query.whoosh_search(filename).all()
    if len(doc)==0:
        resp["message"]="Doc not found"
        resp["status"]=404               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'tags':d.tags,'url':d.docpath,'image':d.imgpath})
        
    return jsonify(resp) 

@app.route('/s1',methods=['GET','POST'])
def s1():
    if request.method=='GET':
        return render_template("search.html")
        

@app.route('/search/docname/<filename>')
def search(filename):
    doc=Docs.query.filter(Docs.docname.like("%"+filename+"%")).all()
    resp={}
   # doc=Documents.query.whoosh_search(filename).all()
    if len(doc)==0:
        resp={'status':404,'message':'Document not found'}               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'url':d.docpath,'image':d.imgpath})
        
    return jsonify(resp) 

@app.route('/search/tags/<tag>') 
def search_by_tag(tag):
    doc=Docs.query.filter(Docs.tags.like("%"+tag+"%")).all()      
    resp={}
    if len(doc)==0:
        resp={'status':404,'message':'Document not found'}               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'url':d.docpath,'image':d.imgpath})
    return jsonify(resp)    

@app.route('/search/author/<name>')
def search_by_author(name):
    doc=Docs.query.filter(Docs.author.like("%"+name+"%")).all()      
    resp={}
    if len(doc)==0:
        resp={'status':404,'message':'Document not found'}               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'url':d.docpath,'image':d.imgpath})
    return jsonify(resp)        

@app.route('/search/publisher/<name>')
def search_by_publisher(name):
    doc=Docs.query.filter(Docs.publisher.like("%"+name+"%")).all()      
    resp={}
    if len(doc)==0:
        resp={'status':404,'message':'Document not found'}               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'url':d.docpath,'image':d.imgpath})
    return jsonify(resp)

def get_extension(filename):
    return filename.rsplit('.',1)[1]

def get_year(date):
    return date.split('-',1)[1]    

@app.route('/search/type/<t>')
def search_by_type(t):
    doc=Docs.query.filter(Docs.filename.like("%."+t)).all()  
    resp={}
    if len(doc)==0:
        resp={'status':404,'message':'Document not found'}               
    else:
        resp["status"]=200
        resp["data"]=[]
        for d in doc:
            resp["data"].append({'id':d.docid,'name':d.docname,'filename':d.filename,'author':d.author,'publisher':d.publisher,'size':d.docsize,'url':d.docpath,'image':d.imgpath})  	

    return jsonify(resp)        
	
if __name__=='__main__':
    app.run(debug=True,threaded=True)	
