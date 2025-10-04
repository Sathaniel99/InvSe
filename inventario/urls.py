from django.urls import path
from . import views
from . import views_jefe_area
from . import views_economico
from . import views_admin

urlpatterns = [
    ####################################################################################################
    ##########################              PAGINAS PRINCIPALES               ##########################
    ####################################################################################################
    # Página de Inicio
    path('', views.home_page, name='home'),

    # ENDPOINTS
    path('alertas-stock-api', views.alertas_stock_api, name='alertas-stock-api'),
    path('alertas-stocks-api-filter', views.alertas_stocks_api_filter, name='alertas-stocks-api-filter'),
    path('alertas-stocks-api-delete/<int:id>', views.alertas_stocks_api_delete, name='alertas-stocks-api-delete'),
    
    # Para pagina en construccion
    # path('/build_page', views.build_page, name='build_page'),
    
    
    ####################################################################################################
    ##########################                 AUTENTICACION                  ##########################
    ####################################################################################################
    path('login/', views.Main_LoginView.as_view(), name='login'),
    path('logout/', views.Main_LogoutView.as_view(), name='logout'),


    # ENDPOINTS
    path('login/password-forgot', views.password_forgot_htmx, name='password-forgot'),
    path('login/login-form', views.login_form_htmx, name='login-form'),

    ####################################################################################################
    ##########################                 CONFIGURACION                  ##########################
    ####################################################################################################
    path('config/', views.self_account_config, name='self-config'),
    path('update-user', views.update_self_user, name='update-self-user'),
    path('update-password', views.update_self_password, name='update-self-password'),
    path('config/update-self-photo', views.update_self_photo, name='update-self-photo'),
        
    ####################################################################################################
    ##########################                   INVENTARIO                   ##########################
    ####################################################################################################
    path('inventario/revisar-inventario/', views.revisar_inventario, name='revisar-inventario'),
    path('inventario/list-inventario/', views.list_inventario, name='list-inventario'),
    path('inventario/read-inventario/<int:id>', views.read_inventario, name='read-inventario'),
    path('inventario/update-inventario/<int:id>', views.update_inventario, name='update-inventario'),
    path('inventario/delete-inventario/<int:id>', views.delete_inventario, name='delete-inventario'),

    ####################################################################################################
    #########################                  ACTIVOS FIJOS                  ##########################
    ####################################################################################################
    path('inventario/sin-local-activos', views.sin_local_activos, name='sin-local-activos'),

    # Vistas para Economico
    path('inventario/entrada-activos', views_economico.entrada_activos, name='entrada-activos'),

    # Vistas para Jefe Área
    path('inventario/ajuste-activos', views_jefe_area.ajuste_activos, name='ajuste-activos'),
    path('inventario/salida-activos/<int:id>', views_jefe_area.salida_activos, name='salida-activos'),
    
    # ENDPOINTS
    path('inventario/sin-local-activos-api/<int:id>', views.sin_local_activos_htmx, name='sin-local-activos-htmx'),
    path('inventario/actual-inventario-api/<int:id>', views.actual_inventario_api, name='actual_inventario_api'),
    path('inventario/revisar-inventario-api/<int:id>', views.revisar_inventario_api, name='revisar_inventario_api'),
    path('inventario/historial-inventario-api/<int:id>', views.historial_inventario_api, name='historial_inventario_api'),

    ####################################################################################################
    #########################                    PRODUCTOS                    ##########################
    ####################################################################################################
    # Vista para Ambos
    path('productos/resumen_productos', views.resumen_productos, name='resumen-productos'),
    
    # Vistas para Economico
    path('productos/create-productos/', views_economico.create_productos, name='create-productos'),
    path('productos/list-productos/', views_economico.list_productos, name='list-productos'),
    path('productos/update-productos/<int:id>', views_economico.update_productos, name='update-productos'),
    path('productos/delete-productos/<int:id>', views_economico.delete_productos, name='delete-productos'),
    path('productos/show-productos/<int:id>', views_economico.show_productos, name='show-productos'),
    path('productos/edit-productos/<int:id>', views_economico.edit_productos, name='edit-productos'),
    
    ####################################################################################################
    ##########################                   SOLICITUDES                  ##########################
    ####################################################################################################
    # Solicitudes Jefe Área
    path('productos/solicitar-productos/', views_jefe_area.solicitar_productos, name='solicitar-productos'),
    path('productos/solicitudes-productos/', views_jefe_area.solicitudes_productos_tabla, name='solicitudes-productos-tabla'),
    path('productos/eliminar-solicitudes-productos-creados/<int:id>', views_jefe_area.eliminar_solicitudes_productos_tabla, name='eliminar-solicitudes-productos-creados'),
    # Solicitudes Economico
    path('productos/solicitados', views_economico.productos_solicitados, name='productos-solicitados'),
    
    # END POINTS
    # URL PARA AMBOS ROLES
    path('productos/ver-solicitud-creada-api/<int:id>', views.ver_solicitud_creada, name='ver-solicitud-creada-api'),
    # Solicitudes Jefe Área
    path('productos/vaciar-carrito/', views_jefe_area.vaciar_carrito_api, name='vaciar-carrito-api'),
    path('productos/preparar_solicitud/<int:id>/<int:cant>', views_jefe_area.preparar_solicitud_api, name='preparar_solicitud-api'),
    path('productos/agregar-item-solicitud-api/<int:id>/<int:cant>', views_jefe_area.agregar_a_la_solicitud_api, name='agregar-item_solicitud-api'),
    path('productos/ver-solicitud-api/', views_jefe_area.ver_solicitud, name='ver_solicitud_api'),
    path('productos/eliminar-item-api/<str:producto_id>/', views_jefe_area.eliminar_item_solicitud_api, name='eliminar-item-solicitud-api'),
    path('productos/confirmar-solicitud-api/', views_jefe_area.confirmar_solicitud_api, name='confirmar-solicitud-api'),
    # Solicitudes Economico
    path('productos/rechazar-solicitud/<int:id>', views_economico.rechazar_solicitud, name='rechazar-solicitud-api'),
    path('productos/aprobar-solicitud/<int:id>', views_economico.aprobar_solicitud, name='aprobar-solicitud-api'),

    ####################################################################################################
    ##########################                  PROVEEDORES                   ##########################
    ####################################################################################################
    # Vistas para Economico
    path('proveedores/resumen-proveedores', views_economico.resumen_proveedores, name='resumen-proveedores'),
    path('proveedores/create-proveedores/', views_economico.create_proveedores.as_view(), name='create-proveedores'),
    path('proveedores/list-proveedores/', views_economico.list_proveedores, name='list-proveedores'),

    # END POINTS
    path('proveedores/update-proveedores/<int:id>', views_economico.update_proveedores, name='update-proveedores-api'),
    path('proveedores/delete-proveedores/<int:id>', views_economico.delete_proveedores, name='delete-proveedores-api'),
    path('proveedores/show-proveedor/<int:id>', views_economico.show_proveedor, name='show-proveedor-api'),
    
    ####################################################################################################
    ##########################                    REPORTES                    ##########################
    ####################################################################################################
    path('reportes/', views.main_reportes, name='reportes'),
    path('reporte-valoracion-economica', views.reporte_valoracion_economica, name='reporte-valoracion-economica'),

    ####################################################################################################
    ##########################                   END POINTS                   ##########################
    ####################################################################################################










    ####################################################################################################
    ##########################                   ADMIN SITE                   ##########################
    ####################################################################################################
    path('server-config/', views_admin.server_config, name='server-config'),
    path('users/manage-users', views_admin.manage_users, name='manage-users'),
    path('users/state-user/<int:id>', views_admin.state_user, name='state-user'),
    path('users/create-user', views_admin.UsuarioCreateView.as_view(), name='create-user'),
    path('users/editar-usuario/<int:id>', views_admin.editar_usuario, name='editar-usuario'),
    path('users/eliminar-usuario/<int:id>', views_admin.eliminar_usuario, name='eliminar-usuario'),

    # END POINTS
    
    path('server-config/update-fields-<int:id>', views_admin.update_acciones_ubicaciones, name='update-acciones-ubicaciones'),
    path('server-config/create-ubicacion', views_admin.create_ubicacion_htmx, name='create-ubicacion-htmx'),
    path('server-config/update-ubicacion', views_admin.update_ubicacion_htmx, name='update-ubicacion-htmx'),
    path('server-config/create-areas', views_admin.create_areas_htmx, name='create-areas-htmx'),
    path('server-config/update-areas', views_admin.update_areas_htmx, name='update-areas-htmx'),
    path('server-config/create-estados', views_admin.create_estados_htmx, name='create-estados-htmx'),
    path('server-config/update-estados', views_admin.update_estados_htmx, name='update-estados-htmx'),
    path('server-config/create-acciones', views_admin.create_acciones_htmx, name='create-acciones-htmx'),
    path('server-config/update-acciones', views_admin.update_acciones_htmx, name='update-acciones-htmx'),

]