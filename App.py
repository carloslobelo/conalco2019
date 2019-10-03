from flask import Flask, render_template,request, redirect, url_for,flash, session
from flask_mysqldb import MySQL
from datetime import datetime
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk import word_tokenize
import string

app=Flask(__name__)
app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['PORT']="3306"
app.config['MYSQL_PASSWORD']=""
app.config['MYSQL_DB']="ent_con_9102"

mysql=MySQL(app)
nomUsuario=''
idEst=''
apelEst=''
nomEst=''
#para la sesion
app.secret_key="llave"

def pExamen(idexamest):
    print("Puntuacion del test")
    curIt=mysql.connection.cursor()
    cur1=mysql.connection.cursor()
    cur1.execute("select * from resp_exam_est where idexamest=%s",{idexamest})
    dResp=cur1.fetchall()
    now = datetime.now()
    hoy = now.strftime('%Y-%m-%d %H:%M:%S')
    rM=[]
    i=0
    valor=0
    sValor=0
    for filaResp in dResp:
        texto=filaResp[3]
        nItem=filaResp[1]
        curIt.execute("select * from opcion  where texto_opcion=%s",{texto})
        d_opcion=curIt.fetchone()
        valor=d_opcion[4]
        
        if valor==0:
            curM=mysql.connection.cursor()
            curM.execute('select * from item where iditem=%s',{nItem})
            dM=curM.fetchone()
            rM.append(dM)
        else:
            sValor=sValor+valor
        
    cur1.execute("UPDATE exam_est SET fecha=%s,valoracion=%s,finalizado=%s WHERE idexamest=%s",(hoy,sValor,1,idexamest))
    mysql.connection.commit()
    cur1.execute("SELECT * FROM exam_est WHERE idexamest=%s",{idexamest})
    dAux=cur1.fetchone()
    return dAux 

def pFelder(id):
        #id -> estudiante 
    act_ref=[1,5,9,13,17,21,25,29,33,37,41]
    sens_int=[2,6,10,14,18,22,26,30,34,38,42]
    visb_verb=[3,7,11,15,19,23,27,31,35,39,43]
    sec_glob=[4,8,12,16,20,24,28,32,36,40,44]
    sumatoria_A=[0,0,0,0]
    sumatoria_B=[0,0,0,0]
    print("Puntuacion del test de felder")
    cur=mysql.connection.cursor()
    cur.execute("select * from exam_est where idest=%s and idexam=%s",(id,"7"))
    dExamEst=cur.fetchone()
    idexamest=dExamEst[0]
    curIt=mysql.connection.cursor()
    cur1=mysql.connection.cursor()
    cur1.execute("select * from resp_exam_est where idexamest=%s",{idexamest})
    dResp=cur1.fetchall()
    respuestas=[]
    i=0
    for filaResp in dResp:
        texto=filaResp[3]
        nItem=filaResp[1]
        curIt.execute("select * from opcion  where texto_opcion=%s",{texto})
        d_opcion=curIt.fetchone()
        valor=d_opcion[4]
        respuestas.append(valor)
        i=i+1
    c=0
    act=0
    sen=0
    vis=0
    sec=0
    print(respuestas)
    while c<i:
        act=act+respuestas[c]
        sen=sen+respuestas[c+1] 
        vis=vis+respuestas[c+2]
        sec=sec+respuestas[c+3]
        c=c+4
    sumatoria_B[0]=act
    sumatoria_B[1]=sen
    sumatoria_B[2]=vis
    sumatoria_B[3]=sec
    sumatoria_A[0]=11-sumatoria_B[0]
    sumatoria_A[1]=11-sumatoria_B[1]
    sumatoria_A[2]=11-sumatoria_B[2]
    sumatoria_A[3]=11-sumatoria_B[3]
    curEstilo=mysql.connection.cursor()
    curEstilo.execute("INSERT INTO estilos_est (idest, act,ref,sens,intuitivo,vis,verbal,sec,global) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(id,sumatoria_A[0],sumatoria_B[0],sumatoria_A[1],sumatoria_B[1],sumatoria_A[2],sumatoria_B[2],sumatoria_A[3],sumatoria_B[3]))
    mysql.connection.commit()
    curEstilo.execute("select * from estilos_est where idest=%s",{id})
    d_estilo=curEstilo.fetchone()
    return d_estilo

def remove_stopwords(word_list):
        processed_word_list = []
        for word in word_list:
            word = word.lower()
            if word not in stopwords.words("spanish"):
                processed_word_list.append(word)
        return processed_word_list

@app.route('/pre_test/<grupo>')
def preTest(grupo):
    cur=mysql.connection.cursor()
    cur.execute("""SELECT estudiante.nomest,estudiante.apelest, item.texto_pregunta,resp_exam_est.texto_resp 
    FROM examen, exam_est,item,resp_exam_est,estudiante 
    WHERE examen.idexam=exam_est.idexam and resp_exam_est.idexamest=exam_est.idexamest
    and examen.idexam=8 and estudiante.idest=exam_est.idest and item.id_exam=examen.idexam""")  
    dResp=cur.fetchall()
    curItems=mysql.connection.cursor()
    curItems.execute("select iditem, texto_pregunta from item where id_exam=8")
    dItems=curItems.fetchall()
    curResp=mysql.connection.cursor()
    dRTotal=[]
    texto=""
    frecuencias=[]
    preguntas=[]
    resps=[]
    for item in dItems:
        codItem=item[0]
        preguntas.append(item[1])
        curResp.execute("select * from resp_exam_est where id_respuesta=%s",{codItem})
        dResp=curResp.fetchall()
        resps.append(dResp)
        for linea in dResp:
            dRTotal.append(linea)
            texto=texto+" "+linea[3]
        tokens = word_tokenize(texto)
        texto=''
        wordList=tokens
        word_list=remove_stopwords(wordList)
        print(word_list)
        fdist = FreqDist(word_list)
        lfrecuencias=''
        for key,val in fdist.items():
            lfrecuencias=lfrecuencias+str(key) + ':' + str(val)+ ' '
            print (str(key) + ':' + str(val))
        vec=lfrecuencias.split()
        frecuencias.append(vec)
    
    textos=dResp
   # all_words = FreqDist(w.lower() for w in dResp[3] if w.lower() not in stop and w.lower() not in string.punctuation)
   # print(all_words)
    return render_template('preconceptos.html',resultado=resps,f=frecuencias,pregs=preguntas)

@app.route('/close')
def closeSesion():
    session.clear()
    return redirect(url_for('ingreso'))


#Guardar Respuestas de Examen
@app.route('/save_exam',methods=['POST'])
def saveExamen():
    now = datetime.now()
    hoy = now.strftime('%Y-%m-%d %H:%M:%S')
    if request.method=='POST':
        idex=request.form['idex']
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM item where id_exam=%s",{idex})
        data=cur.fetchall()
        cod_est=session['idest']
        cur1=mysql.connection.cursor()
        cur1.execute("INSERT INTO exam_est (idexam,idest,fecha,valoracion) VALUES (%s,%s,%s,%s)",(idex,cod_est,hoy,0))
        mysql.connection.commit()
        cur1.execute("select * from exam_est where idest=%s order by idexamest desc",{cod_est})
        d_exam_est=cur1.fetchone()
        idExEst=d_exam_est[0]
        curSave=mysql.connection.cursor()
        for item in data:
            campo='pregs_'+str(item[0])
            valor=request.form[campo]
            curSave.execute("INSERT INTO resp_exam_est(id_respuesta,idexamest,texto_resp) VALUES (%s,%s,%s)",(item[0],idExEst,valor))
        mysql.connection.commit()
        cur1.execute("update exam_est set finalizado=True where idexamest=%s",{idExEst})
        mysql.connection.commit()
        flash("Examen realizado")
        ruta=''
        print("examen %s",idex)
        result=[]
        if idex=='7':
            result=pFelder(cod_est)
            ruta='rfelder.html'
            print(result)
            
        else:
            if idex=='8':
                #result=preTest(idExEst)
                ruta='pre_test.html'
            else:
                result=pExamen(idExEst)
                ruta='puntos.html'
        return render_template(ruta,estilo=result)  


@app.route('/item')
def item():
    cur=mysql.connection.cursor()
    cur.execute("select * from examen")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("select * from item order by id_exam desc")
    data1=cur2.fetchall()
    return render_template("item.html",items=data1,examenes=data)

#agregar item a examen particular
@app.route('/item_exam/<id>')
def item_exam(id):
    cur=mysql.connection.cursor()
    cur.execute("select * from examen where idexam=%s",{id})
    data=cur.fetchone()
    cur2=mysql.connection.cursor()
    cur2.execute("select * from item where id_exam=%s",{id})
    data1=cur2.fetchall()
    return render_template("itemexam.html",items=data1,ex=data)

@app.route('/agregar_item', methods=['POST'])
def agregar_item():
    if request.method=='POST':
        pregunta=request.form['pregunta']
        valor=request.form['valor']
        idexam=request.form['cbidex']
        respuesta=request.form['respuesta']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO item(texto_pregunta, correcta, pregunta_tipo, valor, id_exam, id_objetivo) VALUES (%s, %s,'0', %s, %s,0)",(pregunta, respuesta, valor, idexam))
        mysql.connection.commit()
        msg="El item fue agregado con exito"
        flash(msg)
        return redirect(url_for('item'))



@app.route('/docente')
def docente():
    cursEst=mysql.connection.cursor()
    cursEst.execute("select distinct grupo from estudiante")
    res=cursEst.fetchall()
    return render_template("docente.html",grupos=res)


@app.route('/add_item_ex', methods=['POST'])
def add_item_ex():
    if request.method=='POST':
        pregunta=request.form['pregunta']
        
        idexam=request.form['idex']
        #respuesta=request.form['respuesta']
        respuestas=request.form.getlist('respuestas[]')
        valores=request.form.getlist('valores[]')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO item(texto_pregunta, correcta, pregunta_tipo, valor, id_exam, id_objetivo) VALUES (%s, %s,'0', %s, %s,0)",(pregunta, "si", 0, idexam))
        #cur.execute("INSERT INTO opcion(id_item,texto_opcion,valor) VALUES (%s,%s,%s)",(id_item,texto_opcion,valor))
        mysql.connection.commit()
        cur2=mysql.connection.cursor()
        cur2.execute("select * from item order by iditem desc")
        d_item=cur2.fetchone()
#       guardar opciones de respuesta
        codItem=d_item[0]
        print(codItem)
        i=0
        print("respuestas")
        for respuesta in respuestas:
            cur.execute("INSERT INTO opcion(id_item,texto_opcion,valor) VALUES (%s,%s,%s)",(codItem,respuesta,valores[i]))
            i=i+1

        mysql.connection.commit()
        msg="El item fue agregado con exito"
        flash(msg)
        return redirect(url_for('item_exam',id=idexam))
        


@app.route('/depto')
def depto():
    ruta=''
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM departamento")
    data=cur.fetchall()
    
    if 'usuario' in session:
            print("existe")
            print(session['usuario'])
            if session['usuario']=='u1':
                ruta='depto.html'
            else:
                ruta='ingreso.html'
                data=None
    
    return render_template(ruta,deptos=data)

#Examen
@app.route('/examen')
def examen():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM examen")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM colegio")
    data2=cur2.fetchall()
    return render_template('examen.html',examenes=data,colegios=data2)


#Entrada
@app.route('/usuarios')
def usuario():
    return render_template('entrada.html')


#Ingreso
@app.route('/')
def ingreso():
    return render_template('ingreso.html')


#Ingresar
@app.route('/ingresar', methods=['POST'])
def ingresar():
    if request.method=='POST':
        usuario=request.form['usuario']
        clave=request.form['clave']
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM prueba where pregunta=%s and respuesta=MD5(%s)",(usuario,clave))
        data=cur.fetchone()
        ruta=''
        data1=[]
        grup=0
        if data==None:
                print("Acceso denegado")
                ruta='ingreso.html'
                session.clear()
        else:
                print("Puede pasar")
                ruta='examen.html'
                session['usuario']=usuario
                cur1=mysql.connection.cursor()
                cur1.execute("SELECT * FROM estudiante where idest=%s",{data[4]})
                data1=cur1.fetchone()
                grup=data1[7]
                idEst=data1[0]
                nomUsuario=usuario
                nomEst=data1[2]
                apelEst=data1[3]
                session['nomest']=nomEst
                session['apelest']=apelEst
                session['idest']=idEst
               
    print(data)
    cur.execute("SELECT * FROM examen")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM colegio")
    data2=cur2.fetchall()

    cursEst=mysql.connection.cursor()
    cursEst.execute("select distinct grupo from estudiante")
    res=cursEst.fetchall()
    if grup==17:
        return render_template("docente.html",grupos=res)
    else:
        return render_template(ruta,examenes=data,colegios=data2,est=data1)
    




#Agregar Examen
@app.route('/agregar_examen', methods=['POST'])
def agregar_examen():
    if request.method=='POST':
        titulo=request.form['titulo']
        grado=request.form['grado']
        colegio=request.form['cbidcol']
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO examen(titulo,grado,colegio) VALUES(%s,%s,%s)",(titulo,grado,colegio))
        mysql.connection.commit()
        msg="Los datos del examen ["+titulo+"] se guardaron exitosamente"
        flash(msg)
    return redirect(url_for('examen'))

@app.route('/feditaexamen/<id>')
def feditaexamen(id):
    cursor=mysql.connection.cursor()
    cursor.execute('select * from examen where idexam=%s',{id})
    data = cursor.fetchone()
    cursor=mysql.connection.cursor()
    cursor.execute("select * from colegio")
    data2=cursor.fetchall()
    return render_template('feditaexamen.html',ex=data,colegios=data2)

@app.route('/editar_examen', methods=['POST'])
def edita_examen():
    if request.method=='POST':
        idexam=request.form['idexam']
        titulo=request.form['titulo']
        grado=request.form['grado']
        colegio=request.form['cbidcol']
        cursor=mysql.connection.cursor()
        cursor.execute("UPDATE examen SET titulo = %s, grado=%s, colegio = %s WHERE idexam = %s",(titulo,grado,colegio,idexam))
        mysql.connection.commit()
        msg="Los datos del examen ["+titulo+"] se modificaron exitosamente"
        flash(msg)
    return redirect(url_for('examen'))
    
@app.route('/eliminaexamen/<id>')
def eliminaexamen(id):
    cursor=mysql.connection.cursor()
    cursor.execute("delete from examen where idexam=%s",{id})
    mysql.connection.commit()
    msg="El examén ["+id+"] fue eliminado exitosamente"
    flash(msg)
    return redirect(url_for('examen'))

#ver Examen
@app.route('/f_ver_exam/<id>')
def fVerExamen(id):
    auxEst=[]
    if 'idest' in session:
        curEst=mysql.connection.cursor()
        curEst.execute("select * from estudiante where idest=%s",{session['idest']})
        auxEst=curEst.fetchone()
    print("Estudiante logueado")
    print(auxEst)
    curEx=mysql.connection.cursor()
    curEx.execute("select * from examen where idexam=%s",{id})
    aux=curEx.fetchone()
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM item where id_exam=%s",{id})
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM opcion where id_item in (SELECT iditem FROM item where id_exam=%s)",{id})
    data2=cur2.fetchall()
    return render_template("f_ver_exam.html",d_items=data,d_opciones=data2,ex=aux,est=auxEst)



#Estudiante

@app.route('/estudiante')
def estudiante():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM ciudad")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM estudiante")
    data2=cur2.fetchall()
    cur3=mysql.connection.cursor()
    cur3.execute("SELECT * FROM colegio")
    data3=cur3.fetchall()
    activar='disabled'
    if 'usuario' in session:
        if session['usuario']=='u1':
            activar=' '
    print(activar)
    return render_template("estudiante.html",ciudades=data,estudiantes=data2,colegios=data3,activo=activar)

#Editar estudiante 

@app.route('/feditaestudiante/<id>')
def feditaestudiante(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM ciudad")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM estudiante  WHERE idest=%s",{id})
    data2=cur2.fetchone()
    cur3=mysql.connection.cursor()
    cur3.execute("SELECT * FROM colegio")
    data3=cur3.fetchall()
    return render_template("feditaestudiante.html",ciudades=data,estudiante=data2,colegios=data3)

#editar estudiante
@app.route('/editar_estudiante',methods=['POST'])
def edit_estudiante():
    if request.method=='POST':
        id_ciudad=request.form['cbidciudad']
        idest=request.form['idest']  
        ced_est=request.form['nuip'] 
        nomest=request.form['nomest'] 
        apelest=request.form['apelest'] 
        direst=request.form['direst']
        celest=request.form['celest'] 
        id_ciudad=request.form['cbidciudad'] 
        grado=request.form['grado']
        grupo=request.form['grupo'] 
        fecha_nac=request.form['fecha_nac']  
        id_colegio=request.form['cbidcol'] 
        cursor=mysql.connection.cursor()
        cursor.execute(""" UPDATE estudiante SET ced_est=%s,nomest=%s,apelest= %s,celest =%s,direst=%s ,
        id_ciudad=%s,grado=%s,grupo=%s,fecha_nac=%s,id_colegio=%s
        WHERE idest= %s""",(ced_est,nomest,apelest,celest,direst,id_ciudad,grado,grupo,fecha_nac,id_colegio,idest))
        mysql.connection.commit()
        msg="El Estudiante ["+nomest+" "+apelest+"] fue modificado exitosamente"
        flash(msg)
        return redirect(url_for('estudiante'))

#Agregar estudiante

@app.route('/agregar_estudiante', methods=['POST'])
def add_estudiante():
    if request.method=='POST':
        id_ciudad=request.form['cbidciudad'] 
        ced_est=request.form['nuip'] 
        nomest=request.form['nomest'] 
        apelest=request.form['apelest'] 
        direst=request.form['direst']
        celest=request.form['celest'] 
        email=request.form['email'] 
        clave=request.form['clave'] 
        id_ciudad=request.form['cbidciudad'] 
        grado=request.form['grado']
        grupo=request.form['grupo'] 
        fecha_nac=request.form['fecha_nac']  
        id_colegio=request.form['cbidcol'] 
        cursor=mysql.connection.cursor()
        cursor.execute("""INSERT INTO 
        estudiante(ced_est,nomest,apelest,celest,direst,id_ciudad,grado,grupo,fecha_nac,id_colegio)
        VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s)""", (ced_est,nomest,apelest,celest,direst,id_ciudad,grado,grupo,fecha_nac,id_colegio))
        now = datetime.now()
        hoy = now.strftime('%Y-%m-%d %H:%M:%S')
        mysql.connection.commit()
        cAux=mysql.connection.cursor()
        cAux.execute("select * from estudiante where ced_est=%s",{ced_est})
        dAux=cAux.fetchone()
        cursor.execute("INSERT INTO prueba (pregunta,respuesta,tipo,idest,creado_por,fecha) VALUES (%s, MD5(%s),%s,%s,%s,%s)",(email,clave,17,dAux[0],"root",hoy))
        mysql.connection.commit()
        msg="El Estudiante ["+nomest+" "+apelest+"] fue guardado exitosamente"
        flash(msg)
        return redirect(url_for('estudiante'))


#Acudiente
@app.route('/acudiente')
def acudiente():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM ciudad")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM acudiente")
    data2=cur2.fetchall()
    return render_template("acudiente.html",ciudades=data,acudientes=data2)

#Agregar acudiente

@app.route('/agregar_acudiente', methods=['POST'])
def add_acudiente():
    if request.method=='POST':
        id_ciudad=request.form['cbidciudad'] 
        cedula=request.form['cedula'] 
        nomacu=request.form['nomacud'] 
        apelacud=request.form['apelacud'] 
        diracu=request.form['diracud']
        celacud=request.form['celacud'] 
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO acudiente(cedula, nomacu, apelacud,celacud,diracu,id_ciudad) VALUES(%s,%s,%s,%s,%s,%s)", (cedula, nomacu, apelacud,celacud,diracu,id_ciudad))
        mysql.connection.commit()
        msg="El Acudiente ["+nomacu+" "+apelacud+"] fue guardado exitosamente"
        flash(msg)
        return redirect(url_for('acudiente'))


#Elimina acudiente

@app.route('/eliminaacudiente/<id>')
def elimina_acudiente(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM acudiente WHERE idacudiente=%s", {id})
    mysql.connection.commit()
    flash("El acudiente fue eliminado")
    return redirect(url_for('acudiente'))

#Edita acudiente

@app.route('/feditaacudiente/<id>')
def feditacudiente(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM ciudad")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM acudiente  WHERE idacudiente=%s",{id})
    data2=cur2.fetchone()
    print(data)
    return render_template("feditaacudiente.html",ciudades=data,acudiente=data2)


@app.route('/modificar_acudiente',methods=['POST'])
def edita_acudiente():
     if request.method=='POST':
        idacudiente=request.form['idacudiente'] 
        id_ciudad=request.form['cbidciudad'] 
        cedula=request.form['cedula'] 
        nomacu=request.form['nomacud'] 
        apelacud=request.form['apelacud'] 
        diracu=request.form['diracud']
        celacud=request.form['celacud'] 
        cur=mysql.connection.cursor()
        
        cur.execute("UPDATE acudiente SET cedula =%s,nomacu =%s,apelacud=%s,celacud =%s,diracu=%s, id_ciudad =%s WHERE idacudiente=%s",(cedula, nomacu, apelacud,celacud,diracu,id_ciudad,idacudiente))
        mysql.connection.commit()
        msg="El Acudiente ["+nomacu+" "+apelacud+"] fue modificado exitosamente"
        flash(msg)
        return redirect(url_for('acudiente'))



@app.route('/ciudad')
def ciudad():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM departamento")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM ciudad")
    data2=cur2.fetchall()
    return render_template("ciudad.html",deptos=data,ciudades=data2)



#Agregar ciudad
@app.route('/agregar_ciudad', methods=['POST'])
def add_ciudad():
    if request.method=='POST':
        nomciudad=request.form['nomciudad'] 
        id_depto=request.form['cbiddepto']       
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO ciudad(nomciudad,id_depto) VALUES(%s,%s)", (nomciudad,id_depto))
        mysql.connection.commit()
        msg="La  ciudad llamada "+nomciudad+" fue guardada exitosamente"
        flash(msg)
        
    return redirect(url_for('ciudad'))
       
#/eliminaciudad

@app.route('/eliminaciudad/<id>')
def elimina_ciudad(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM ciudad WHERE id_ciudad=%s", {id})
    mysql.connection.commit()
    flash("La ciudad fue eliminada")
    return redirect(url_for('ciudad'))

#Edita ciudad

@app.route('/feditaciudad/<id>')
def feditaciudad(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM departamento")
    data=cur.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM ciudad  WHERE id_ciudad=%s",{id})
    data2=cur2.fetchone()
    print(data)
    return render_template("feditaciudad.html",dptos=data,ciud=data2)

@app.route('/edita_ciudad',methods=['POST'])
def edita_ciudad():
     if request.method=='POST':
        nomciudad=request.form['nomciudad'] 
        iddepto=request.form['cbiddepto'] 
        id_ciudad=request.form['idciudad']
        cur=mysql.connection.cursor()
        cur.execute("UPDATE ciudad SET nomciudad=%s, id_depto=%s WHERE id_ciudad=%s", (nomciudad,iddepto,id_ciudad))
        mysql.connection.commit()
        msg="La ciudad  ["+nomciudad+"] fue modificada con exito"
        flash(msg)
        return redirect(url_for('ciudad'))


@app.route('/feditadepto/<id>')
def feditadepto(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM departamento WHERE iddepto=%s",{id})
    data=cur.fetchone()
    return render_template("feditadepto.html",fila=data)

@app.route('/eliminadepto/<id>')
def elimina_depto(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM departamento WHERE iddepto=%s", {id})
    mysql.connection.commit()
    flash("El departamento fue eliminado")
    return redirect(url_for('depto'))


@app.route('/edita_depto',methods=['POST'])
def edita_depto():
     if request.method=='POST':
        nomdepto=request.form['nomdepto'] 
        iddepto=request.form['iddepto'] 
        cur=mysql.connection.cursor()
        cur.execute("UPDATE departamento SET nomdepto=%s WHERE iddepto=%s", (nomdepto,iddepto))
        mysql.connection.commit()
        msg="El departamento "+[nomdepto]+" fue modificado con exito"
        flash(msg)
        return redirect(url_for('depto'))

@app.route('/agregar_depto', methods=['POST'])
def add_depto():
    if request.method=='POST':
        nomdepto=request.form['nomdepto']       
        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO departamento(nomdepto) VALUES(%s)", {nomdepto})
        mysql.connection.commit()
        flash("El departamento fue guardado")
        
    return redirect(url_for('depto'))
       

@app.route('/edit')
def edit():
    return "Editado"


@app.route('/delete')
def delete():
    return "Eliminado"


if __name__=='__main__':
    app.run(port=3000,debug=True)

