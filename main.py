from kivymd.app import MDApp,App
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton,MDIconButton
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.dropdownitem import MDDropDownItem

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp

import mysql.connector
import pymysql


Window.keyboard_amin_args = {'d': .2, 't':'in_out_expo'}
Window.softimput_mode = "below_target"

host = '190.228.29.68'
user = 'g24'
password = 'Enero01..'
dbname = 'saig24'
dbname1 = 'cadenag24'

class WindowManager(MDScreenManager):
    """ Window Manager """
    pass

class Ui(MDScreen):
    pass

class Entrada(MDScreen):
    pass

class Login(MDScreen):
    pass

class LoginApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.control=0
        self.var_pdv=''
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.accent_palette = "Red"

        query = "SELECT count(*),nivel FROM abempleados_usua"
        try:
            self.conect_db = mysql.connector
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            cursor.execute(query)
        except:
            try:
                self.conect_db = pymysql
                db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
                cursor = db.cursor()
                cursor.execute(query)
            except:
                self.show_message_box("Problemas con la conexion")

        db.close()
        
    def build(self):
        return Builder.load_file("entrada.kv")
        
    def connect(self):  # Carga la informacion de Usuarios y Claves
        #optener el user and password del Screen
        app = App.get_running_app()
        self.input_usuario = app.root.get_screen('login').ids['user'].text
        self.input_password = self.root.get_screen('login').ids['password'].text

        #conectar con MySQL
        try:
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            #run query to check user/password
            query = "SELECT count(*),nivel FROM abempleados_usua where username='"+str(self.input_usuario).upper()+"' and password='"+str(self.input_password)+"'"
            cursor.execute(query)
        
            usuario = cursor.fetchone()
            self.nivel=usuario[1]

            count = usuario[0]
            #validar user/password
            if count == 0:
                toast('Usuario o Clave Incorrecta')
            else:
                #toast('CorrectO')
                #guardar en el historico el ingresos la fecha y hora
                query = f"INSERT INTO aapp_historico (username,descripcion) VALUES ('{self.input_usuario.upper()}','INGRESO') "
                cursor.execute(query)
                db.commit()
                self.root.current = "ui"
            
            db.close()
        except:
            self.show_message_box('No se pudo conectar a la Base de Datos')

    def cerrar_tabla(self):  # Cierra las ventanas Activas
        try:
            self.root.get_screen('ui').ids.nav_drawer.set_state("close")
            self.root.get_screen('ui').ids.screen_buscar.clear_widgets()
            self.root.get_screen('ui').ids.screen_tabla.remove_widget(self.table)
        except:
            pass
    
    def show_message_box(self,mensaje):
        dialog = MDDialog(
                        title="Informacion",
                        text=mensaje,
                        buttons=[
                            MDFillRoundFlatButton(text='Cerrar',on_release= lambda x: cerrar())
                            ]
                        )
        dialog.open()

        def cerrar():
            dialog.dismiss()

        
    def ver_tabla_pdv(self):  # Carga la BD de los PDV
        self.cerrar_tabla()
        if "PDV" in self.nivel or "ALTO" in self.nivel :
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            query = "SELECT nombre,grupo FROM aarchivos WHERE estado='ACTIVO' order by nombre "
            cursor.execute(query)
            self.lista_pdv = cursor.fetchall()
            db.close()
            
            self.table = MDDataTable(
                                    pos_hint={'center_y': 0.5, 'center_x': 0.5},
                                    size_hint=(0.8, 0.7),
                                    use_pagination=True,
                                    check=False,
                                    background_color_header="#14888b",
                                    background_color_selected_cell="#424e5e",
                                    rows_num=100,
                                    column_data=[("PDV", dp(90)), ("Grupo", dp(20))],
                                    row_data=[(i[:][0],i[:][1],) for i in self.lista_pdv],
                                    )
            self.table.bind(on_row_press=lambda instance, row: row_selected(instance, row))
            self.root.get_screen('ui').ids['screen_tabla'].add_widget(self.table)

            def row_selected( instance_table, instance_row):  # Selecciona el PDV
                self.var_pdv = instance_row.text
                ver_tabla_precio(self.var_pdv,'','')
        else:
            self.show_message_box('El Usuario no esta Habilitado en esta Opcion')
        
        def ver_tabla_precio(pdv,art,cod):  # Carga la BD de los Articulos de los PDV
            self.cerrar_tabla()
            
            des_articulo = MDTextField(
                                    id='articulo',
                                    font_size=50,
                                    hint_text="Artículo",
                                    icon_left="basket",
                                    size_hint=(.55, .8),
                                    mode="fill",
                                    pos_hint={"center_x": .5, "center_y": .80},
                                    )
            self.root.get_screen('ui').ids.screen_buscar.add_widget(des_articulo)
            
            cod_articulo = MDTextField(
                                    id='codigo',
                                    font_size=50,
                                    hint_text="Código",
                                    icon_left="barcode",
                                    size_hint=(.45, .8),
                                    mode="fill",
                                    pos_hint={"center_x": .5, "center_y": .80},
                                    )
            self.root.get_screen('ui').ids.screen_buscar.add_widget(cod_articulo)
            
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname1)
            cursor = db.cursor()

            query = f""" SELECT a.DESCRIPCION, Round(a.PRECIO,-1), a.STOCK_GRANDE, a.CODIGO ,b.nombre
                            FROM cadenag24.articulo as a 
                            left join saig24.aarchivos as b on a.WEB_SUCURSAL = b.codigo 
                            WHERE b.nombre='{pdv}' and a.DESCRIPCION like '%{art}%' and a.CODIGO like '%{cod}%' order by a.DESCRIPCION"""
            
            cursor.execute(query)
            lista_articulos = cursor.fetchall()
            db.close()

            self.table = MDDataTable(
                                    pos_hint={'center_y': 0.43, 'center_x': 0.5},
                                    size_hint=(0.8, 0.57),
                                    use_pagination=True,
                                    check=False,
                                    background_color_header="#14888b",
                                    background_color_selected_cell="#424e5e",
                                    rows_num=100,
                                    column_data=[("Descripcion", dp(55)), ("Precio", dp(20)), ("Stock", dp(10)), ("Codigo", dp(25)), ("PDV", dp(30))],
                                    row_data=[(i[:][0], i[:][1], i[:][2], i[:][3], i[:][4],) for i in lista_articulos],
                                    )
            self.root.get_screen('ui').ids.screen_tabla.add_widget(self.table)
            
            bt_buscar = MDFillRoundFlatButton(
                                            text="Buscar",
                                            size_hint=(.3, .083),
                                            pos_hint={"center_x": .5, "center_y": .832},
                                            on_release= lambda x: row_selected_1()
                                            )
            self.root.get_screen('ui').ids.screen_buscar.add_widget(bt_buscar)

            def row_selected_1():  # Selecciona el PDV y filtra los Articulos
                if self.var_pdv=='':
                    toast('Tiene que seleccionar un PDV')
                else:
                    ver_tabla_precio(self.var_pdv, des_articulo.text, cod_articulo.text)

    def enviar_mensaje(self):  # Mandar Mensaje s ls BD
        self.cerrar_tabla()
        if "PDV" in self.nivel or "ALTO" in self.nivel :
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            query = "SELECT codigo,nombre,grupo FROM aarchivos WHERE estado='ACTIVO' order by nombre "
            cursor.execute(query)
            self.lista_pdv = cursor.fetchall()
            db.close()
            
            self.table = MDDataTable(
                                    pos_hint={'center_y': 0.5, 'center_x': 0.5},
                                    size_hint=(0.8, 0.7),
                                    use_pagination=True,
                                    check=False,
                                    background_color_header="#14888b",
                                    background_color_selected_cell="#424e5e",
                                    rows_num=100,
                                    column_data=[("COD", dp(20)), ("PDV", dp(90)), ("Grupo", dp(20))],
                                    row_data=[(i[:][0],i[:][1],i[:][2],) for i in self.lista_pdv],
                                    )
            self.table.bind(on_row_press=lambda instance, row: row_selected(instance, row))
            self.root.get_screen('ui').ids['screen_tabla'].add_widget(self.table)

        else:
            self.show_message_box('El Usuario no esta Habilitado en esta Opcion')

        def row_selected( instance_table, instance_row):  # Selecciona el PDV
            self.cod_pdv=self.table.row_data[instance_row.index][0]
            self.var_pdv = instance_row.text
            captura_entry()

        def captura_entry():
            self.cerrar_tabla()
            
            box_problemas= MDBoxLayout(
                                    orientation="vertical",
                                    spacing="28dp",
                                    adaptive_height=True,
                                    size_hint_x=.8,
                                    pos_hint={"center_x": .5, "center_y": .5},
                                    )
            
            pdv=ComboBox(
                        conect_db=self.conect_db,
                        size_hint_x=None,
                        width=200,
                        size_hint=(.8, .18),
                        pos_hint = {'center_x': 0.5, 'y': 0.8}
                        )

            problemas= MDTextField(
                                    id='problemas',
                                    max_height= "130",
                                    multiline= True,
                                    hint_text="Problema",
                                    icon_left="text-box-edit-outline",
                                    size_hint=(.8, .18),
                                    mode="fill",
                                    pos_hint={"center_x": .5, "center_y": .84},
                                    )
            
            observaciones= MDTextField(
                                    id='observaciones',
                                    max_height= "130dp",
                                    multiline= True,
                                    hint_text="Observacion",
                                    icon_left="text-box-edit-outline",
                                    size_hint=(.8, .18),
                                    mode="fill",
                                    pos_hint={"center_x": .5, "center_y": .84},
                                    )
            
            bt_enviar = MDFillRoundFlatButton(
                                            text="Enviar",
                                            size_hint=(.4, .18),
                                            pos_hint={"center_x": .5, "center_y": .84},
                                            on_release=lambda x: guardar(pdv,problemas,observaciones)
                                            )
            
            box_problemas.add_widget(pdv)
            box_problemas.add_widget(problemas)
            box_problemas.add_widget(observaciones)
            box_problemas.add_widget(bt_enviar)

            self.root.get_screen('ui').ids.screen_buscar.add_widget(box_problemas)

        def guardar(pdv,problemas,observaciones):
            if pdv.cod_dpto>0 and len(problemas.text)>0:
                self.cerrar_tabla()
                db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
                cursor = db.cursor()
                query = f"INSERT INTO abpdv_supervisor (idarchivos,iddepartamento,problemas,quien_formula,observaciones) VALUES ({int(self.cod_pdv)},'{pdv.cod_dpto}','{problemas.text}','{str(self.input_usuario).upper()}','{observaciones.text}') "
                cursor.execute(query)
                db.commit()
                db.close()
            else:
                self.show_message_box('Tiene que seleccionar un Departamento y plantear un Problema')
            

        class ComboBox(MDRelativeLayout):
            def __init__(self, conect_db, **kwargs):
                super().__init__(**kwargs)
                self.conect_db=conect_db
                self.cod_dpto=0
                
                # Crear el BoxLayout interno
                self.box = MDBoxLayout(orientation='horizontal', size_hint_y=None,  height=50, spacing=5, md_bg_color='blue')
                
                # Crear el TextInput de KivyMD
                self.dpto = MDTextField(
                                        icon_left="text-box-check-outline",
                                        hint_text="Seleccione un Dpto.",
                                        size_hint=(.8, .18),
                                        mode="fill",
                                        pos_hint={"center_x": .5, "center_y": .55},
                                        )
                
                self.btn = MDDropDownItem(
                    pos_hint={"center_x": .5, "center_y": .5},
                    on_release=self.open_menu,
                )
                
                # Añadir widgets al BoxLayout
                self.box.add_widget(self.dpto)
                self.box.add_widget(self.btn)
                
                # Añadir BoxLayout al ComboBox
                self.add_widget(self.box)
            
            def open_menu(self, item):
                db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
                cursor = db.cursor()
                query = "SELECT * FROM abtipo_departamento order by descripcion "
                cursor.execute(query)
                lista_dpto = cursor.fetchall()
                db.close()
                menu_items = [
                                {
                                    "text": f"{str(i[0])} - {i[1]}",
                                    "on_release": lambda x=f"{i[0]} - {i[1]}": self.set_text(x),
                                } for i in lista_dpto
                            ]
                MDDropdownMenu(caller=item, items=menu_items, md_bg_color=(0, 0.5, 0.5, 1), position="bottom").open()
            
            def set_text(self, value):
                self.dpto.text = value[4:]
                self.cod_dpto=int(value[0:2])

    def ver_problemas_supervisor(self):  # Mandar Mensaje s ls BD
        self.cerrar_tabla()
        if "PDV" in self.nivel or "ALTO" in self.nivel :
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            query = f"SELECT pdv,departamento,problemas,quien_responde,recomendaciones FROM consul_pdv_supervisor where quien_formula='{self.input_usuario.upper()}' order by departamento "
            cursor.execute(query)
            self.lista_problemas = cursor.fetchall()
            db.close()
            
            self.table = MDDataTable(
                                    pos_hint={'center_y': 0.5, 'center_x': 0.5},
                                    size_hint=(0.8, 0.7),
                                    use_pagination=True,
                                    check=False,
                                    background_color_header="#14888b",
                                    background_color_selected_cell="#424e5e",
                                    rows_num=100,
                                    column_data=[("PDV", dp(30)), ("Departamento", dp(30)), ("Problemas", dp(50)), ("Responde", dp(20)), ("Recomendaciones", dp(50))],
                                    row_data=[(i[:][0],i[:][1],i[:][2],i[:][3],i[:][4],) for i in self.lista_problemas],
                                    )
            self.root.get_screen('ui').ids['screen_tabla'].add_widget(self.table)
        else:
            self.show_message_box('El Usuario no esta Habilitado en esta Opcion')

    def ver_problemas_mantenimiento(self):  # Mandar Mensaje s ls BD
        self.cerrar_tabla()
        if "PDV" in self.nivel or "ALTO" in self.nivel :
            db = self.conect_db.connect(host=host,  user=user,  password=password,  database=dbname)
            cursor = db.cursor()
            query = f"SELECT pdv,departamento,problemas,quien_responde,recomendaciones FROM consul_pdv_supervisor where departamento='MANTENIMIENTO' order by created "
            cursor.execute(query)
            self.lista_problemas = cursor.fetchall()
            db.close()
            
            self.table = MDDataTable(
                                    pos_hint={'center_y': 0.5, 'center_x': 0.5},
                                    size_hint=(0.8, 0.7),
                                    use_pagination=True,
                                    check=False,
                                    background_color_header="#14888b",
                                    background_color_selected_cell="#424e5e",
                                    rows_num=100,
                                    column_data=[("PDV", dp(30)), ("Departamento", dp(30)), ("Problemas", dp(50)), ("Responde", dp(20)), ("Recomendaciones", dp(50))],
                                    row_data=[(i[:][0],i[:][1],i[:][2],i[:][3],i[:][4],) for i in self.lista_problemas],
                                    )
            self.root.get_screen('ui').ids['screen_tabla'].add_widget(self.table)
        else:
            self.show_message_box('El Usuario no esta Habilitado en esta Opcion')
                    
if __name__ == "__main__":
    LoginApp().run()


