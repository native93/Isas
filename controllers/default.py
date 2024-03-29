# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################a################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
#def login():
#    form=SQLFORM_factory(db.Field('username','string',requires=IS_NOT_EMPTY()),
#                       db.Field('password','password',requires=IS_NOT_EMPTY()))
#    if form.accepts(request.vars,session):
#        x=db((db.admin.username==form.vars.username)&(db.auth_admin.password==form.vars.password)).select()
#        y=db((db.student.username==form.vars.username)&(db.student.password==form.vars.password)).select()
#    elif form.errors:
#        response.flash='Errors in form'
#    return dict(form=form)
from gluon import current
auth.settings.register_next=URL('student_details')
#if auth.settings.membership=='admin':
#	auth.settings.login_next = URL('admin_interface')
#else:
#	auth.settings.login_next = URL('index')
def groupadd(check_group):
		if not db(db.auth_group.role==check_group).count():
				db.auth_group.insert(role=check_group)
@auth.requires_login()
def student_details():
    groupadd('students')
    auth.add_membership(auth.id_group('students'),session.user_id)
    session.user_id=auth.user.id
    session.user_name=auth.user.first_name
    form=SQLFORM.factory(
        Field('roll_no','integer',length=9,requires=IS_NOT_EMPTY()),
        Field('year_join',length=4,requires=IS_NOT_EMPTY()),
        Field('full_name','string',requires=IS_NOT_EMPTY()),
        Field('branch',requires=IS_IN_SET(['CSD','CSE','ECE','ECD','EHD','CLD','CND'])))
    if form.accepts(request.vars,session):
        db.student_det.insert(user_id=auth.user.id,roll_no=form.vars.roll_no,year_join=form.vars.year_join,full_name=form.vars.full_name, branch=form.vars.branch)
        redirect(URL('index'))
    elif form.errors:
        response.flash="errors in forms"
    return dict(form=form)
import datetime
@auth.requires_login()    
def index():
    session.user_id=auth.user.id
    session.user_name=auth.user.first_name
    if auth.has_membership(role='admin'):
        #var=1
        redirect(URL('admin_interface'))
    s=db(db.timing.id>0).select(db.timing.from_1,db.timing.to_1)
    s=s[0]
    f=0
    if (datetime.datetime.now()>s.from_1)&(datetime.datetime.now()<s.to_1):
        f=1
    else:
        f=0
	year=db(db.student_det.user_id==auth.user.id).select(db.student_det.year_join)
	year=int(year[0].year_join)
	x=2*(datetime.date.today().year-year)
	mon=datetime.date.today().month
	if mon>=1 and mon<=7:
		session.sem=x
	else:
		session.sem=x+1
	if session.sem>8:
		session.sem=8
    #print var
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to Isas portal!!")
    return dict(f=f)
@auth.requires_login()
@auth.requires_membership('admin')
def admin_interface():
    #form=SQLFORM.factory(
     #   Field('options',requires=IS_IN_SET(['timing']),widget=SQLFORM.widgets.radio.widget))
    #if form.accepts(request.vars,session):
     #   if request.vars.options=='timing':
      #      redirect(URL('portal_timing'))
    return dict()
@auth.requires_login()
@auth.requires_membership('admin')
def portal_timing():
#    form=SQLFORM(db.timing)
    form=SQLFORM.factory(
        Field('from_1','datetime',requires=IS_NOT_EMPTY(),label="From"),
        Field('to_1','datetime',requires=IS_NOT_EMPTY(),label="To"))
    if form.accepts(request.vars,session):
        #s=db(db.timing.id>0).select()
        if db(db.timing.id>0).count():
            s=db(db.timing.id>0).select(db.timing.id)
            s=s[0]
            db(db.timing.id==s).update(from_1 = form.vars.from_1,to_1 = form.vars.to_1)
        else:
            db.timing.insert(from_1=form.vars.from_1,to_1=form.vars.to_1)
        response.flash=T("timing updated")
    elif form.errors:
        response.flash="errors in forms"  
    return dict(form=form)
@auth.requires_login()
@auth.requires_membership('admin')
def add_grades():
     form=SQLFORM.factory(
     Field('course_id',db.course,requires=IS_IN_DB(db,'course.id','course.name')))
     if form.accepts(request.vars,session):
         redirect(URL('add_grades_1',args=form.vars.course_id))
     elif form.errors:
         response.flash="Errors in form!! "
     return dict(form=form) 
@auth.requires_login()
@auth.requires_membership('admin')
def add_grades_1():
    course_id=request.args(0)
    stu=db((course_id==db.grade.course_id)&(db.grade.student_id==db.student_det.user_id))
    name=db(course_id==db.course.id).select(db.course.name)
    name=name[0]
    form=SQLFORM.factory(
        Field('student_id',db.student_det,requires=IS_IN_DB(stu,'student_det.user_id','student_det.full_name')),
        Field('grade',requires=IS_IN_SET(['A','A-','B','B-','C','C-','D','F'])))
    if form.accepts(request.vars,session):
         db((db.grade.student_id==form.vars.student_id)&(db.grade.course_id==course_id)).update(grade=form.vars.grade)
         response.flash="Grade Updated"
    elif form.errors:
         response.flash="Errors in form!! "
    return dict(form=form,name=name)
@auth.requires_login()
@auth.requires_membership('admin')
def add_courses():
    form=SQLFORM(db.course)
    if form.accepts(request.vars,session):
        response.flash="Course added Successfully"
    elif form.errors:
        response.flash="Errors in form!! "
    return dict(form=form)
@auth.requires_login()
def register():
     #   if form.accepts(request.vars,session) :
     #       response.flash='Entry recorded !!'
     #   elif form.errors:
     #       response.flash='Error in forms !! Please fill it again'
	courses=db(db.course.id>0).select(db.course.name,db.course.code,db.course.credits,db.course.id)
        #myrecords=db(db.grade.id>0).select(db.course)
	courses_reg=db((auth.user.id==db.grade.student_id)).select(db.grade.course_id,db.grade.grade)
	#courses_reg=courses_reg[0]
	session.list_courses=[]
	if request.vars:
		for i in courses:
			id1=str(i.id)
                #session.c=len(request.vars.values())
			if request.vars[id1]:
                    #session.a=request.vars.values()
				value=request.vars[id1]#['%r'%i.id]#[i.id]
                    #session.d=value
				if value=="Yes":
                       #session.b=1
					session.list_courses.append(i.id)
		redirect(URL('show_courses'))
     #elif form.errors:
      #   response.flash='Error in forms !! Please fill it again'
	return dict(courses=courses,courses_reg=courses_reg)
import datetime                  
@auth.requires_login()
def show_courses():
    #courses=[]
    year=db(db.student_det.user_id==auth.user.id).select(db.student_det.year_join)
    year=int(year[0].year_join)
    x=2*(datetime.date.today().year-year)
    mon=datetime.date.today().month
    if (mon>=1) and (mon<=7):
        session.sem=x
    else:
        session.sem=x+1
    if session.sem>8:
        session.sem=8
    courses_reg=db((auth.user.id==db.grade.student_id)).select(db.grade.course_id)
    l=[]
    for i in courses_reg:
        l.append(i.course_id)
    for i in session.list_courses:
        if i not in l:
            db.grade.insert(student_id=auth.user.id,course_id=i,sem=session.sem)
        else:
            db((db.grade.student_id==auth.user.id)&(db.grade.course_id==i)).update(grade=None,sem=session.sem)
    courses=db((db.grade.student_id==auth.user.id)&(db.course.id==db.grade.course_id)&(db.grade.sem==session.sem)).select(db.course.name)
       # courses.append(str(course['name']))
    #courses=db(db.course.id==session.list_courses).select(db.course.name)
    return dict(courses=courses)
@auth.requires_login()
def view_grades():
	grd=db((auth.user.id==db.grade.student_id)&(db.course.id==db.grade.course_id)&(db.grade.sem==session.sem)).select(db.course.name,db.grade.grade,db.course.credits)
	det=db((auth.user.id==db.student_det.user_id)).select(db.student_det.full_name,db.student_det.branch,db.student_det.roll_no)
	grd1=db((auth.user.id==db.grade.student_id)&(db.course.id==db.grade.course_id)).select(db.course.name,db.grade.grade,db.course.credits)
	det=db((auth.user.id==db.student_det.user_id)).select(db.student_det.full_name,db.student_det.branch,db.student_det.roll_no)
	det=det[0]
	c,tc=0.0,0
	for i in grd:
			if(i.grade.grade=='A'):
				tc+=i.course.credits
				c+=i.course.credits*10
			elif i.grade.grade=='A-':
				tc+=i.course.credits
				c+=i.course.credits*9
			elif(i.grade.grade=='B'):
				tc+=i.course.credits
				c+=i.course.credits*8
			elif(i.grade.grade=='B-'):
				tc+=i.course.credits
				c+=i.course.credits*7
			elif(i.grade.grade=='C'):
				tc+=i.course.credits
				c+=i.course.credits*6
			elif(i.grade.grade=='C-'):
				tc+=i.course.credits
				c+=i.course.credits*5
			elif(i.grade.grade=='D'):
				tc+=i.course.credits
				c+=i.course.credits*4
			elif(i.grade.grade=='F'):
				tc+=i.course.credits
				c+=i.course.credits*3
	year=db(db.student_det.user_id==auth.user.id).select(db.student_det.year_join)
	year=int(year[0].year_join)
	x=2*(datetime.date.today().year-year)
	mon=datetime.date.today().month
	if (mon>=1) and (mon<=7):
		session.sem=(x)
	else:
		session.sem=(x+1)
	if session.sem>8:
		session.sem=8
	sg=0
	if(c==0):
		sg="N.A"
	else:
		sg="%0.2f"%float(c/tc)
	session.s=sg
	for i in grd1:
			if(i.grade.grade=='A'):
				tc+=i.course.credits
				c+=i.course.credits*10
			elif i.grade.grade=='A-':
				tc+=i.course.credits
				c+=i.course.credits*9
			elif(i.grade.grade=='B'):
				tc+=i.course.credits
				c+=i.course.credits*8
			elif(i.grade.grade=='B-'):
				tc+=i.course.credits
				c+=i.course.credits*7
			elif(i.grade.grade=='C'):
				tc+=i.course.credits
				c+=i.course.credits*6
			elif(i.grade.grade=='C-'):
				tc+=i.course.credits
				c+=i.course.credits*5
			elif(i.grade.grade=='D'):
				tc+=i.course.credits
				c+=i.course.credits*4
			elif(i.grade.grade=='F'):
				tc+=i.course.credits
				c+=i.course.credits*3
	cg=0
	if(c==0):
		cg="N.A"
	else:
		cg="%0.2f"%float(c/tc)
	session.c=cg
	l=[]
	for i in range(1,session.sem):
		l.append(i)
	l=set(l)
	form=SQLFORM.factory(
		Field('sem',requires=IS_IN_SET(l),widget=SQLFORM.widgets.radio.widget,label="Sems"))
	if form.accepts(request.vars,session):
		redirect(URL('view_grades_1',args=form.vars.sem))
	return dict(grd=grd,det=det,sg=sg,form=form)
@auth.requires_login()
def view_grades_1():
	sem=request.args(0)
	grd=db((auth.user.id==db.grade.student_id)&(db.course.id==db.grade.course_id)&(db.grade.sem==sem)).select(db.course.name,db.grade.grade,db.course.credits)
	det=db((auth.user.id==db.student_det.user_id)).select(db.student_det.full_name,db.student_det.branch,db.student_det.roll_no)
	det=det[0]	
	c,tc=0.0,0
	for i in grd:
			if(i.grade.grade=='A'):
				tc+=i.course.credits
				c+=i.course.credits*10
			elif i.grade.grade=='A-':
				tc+=i.course.credits
				c+=i.course.credits*9
			elif(i.grade.grade=='B'):
				tc+=i.course.credits
				c+=i.course.credits*8
			elif(i.grade.grade=='B-'):
				tc+=i.course.credits
				c+=i.course.credits*7
			elif(i.grade.grade=='C'):
				tc+=i.course.credits
				c+=i.course.credits*6
			elif(i.grade.grade=='C-'):
				tc+=i.course.credits
				c+=i.course.credits*5
			elif(i.grade.grade=='D'):
				tc+=i.course.credits
				c+=i.course.credits*4
			elif(i.grade.grade=='F'):
				tc+=i.course.credits
				c+=i.course.credits*3
	sg=0
	if(c==0):
		sg="N.A"
	else:
		sg="%0.2f"%float(c/tc)
	return dict(grd=grd,det=det,sg=sg,sem=sem)
@auth.requires_login()
def report_make():
	sem=request.args(0)
	sg=request.args(1)
 	grd=db((auth.user.id==db.grade.student_id)&(db.course.id==db.grade.course_id)&(db.grade.sem==sem)).select(db.course.name,db.grade.grade,db.course.credits)
	det=db((auth.user.id==db.student_det.user_id)).select(db.student_det.full_name,db.student_det.branch,db.student_det.roll_no)
	det=det[0]
	html=response.render('default/report.html',dict(grd=grd,det=det,sg=sg,sem=sem))
	return plugin_appreport.REPORTPISA(html=html)
@auth.requires_login()
def mail_send():
		s=str(auth.user.email)
		sem=request.args(0)
		sg=request.args(1)
 		grd=db((auth.user.id==db.grade.student_id)&(db.course.id==db.grade.course_id)&(db.grade.sem==sem)).select(db.course.name,db.grade.grade,db.course.credits)
		det=db((auth.user.id==db.student_det.user_id)).select(db.student_det.full_name,db.student_det.branch,db.student_det.roll_no)
		det=det[0]
		html=response.render('default/report.html',dict(grd=grd,det=det,sg=sg,sem=sem))
		if mail.send(to=[s],
				subject='Grades',
				message=html):
				f=1
				response.flash='Mail Sent'
		else:
				f=0
				response.flash='Failed'
		return dict(f=f)
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
