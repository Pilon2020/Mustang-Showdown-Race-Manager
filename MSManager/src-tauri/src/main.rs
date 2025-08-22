#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
  // Emitter,                   // remove if not emitting
  Manager,                      // needed for get_webview_window()
  WebviewUrl,
  WebviewWindowBuilder,
  menu::{MenuBuilder, MenuItemBuilder, PredefinedMenuItem, SubmenuBuilder},
};

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      // --- App menu (About/Preferences/etc.) ---
      let app_menu = SubmenuBuilder::new(app, "Race Manager")
        .item(&PredefinedMenuItem::about(app, None, None)?)
        .separator()
        .item(&MenuItemBuilder::new("Preferences…").id("preferences").accelerator("CmdOrCtrl+,").build(app)?)
        .separator()
        .item(&PredefinedMenuItem::services(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::hide(app, None)?)
        .item(&PredefinedMenuItem::hide_others(app, None)?)
        .item(&PredefinedMenuItem::show_all(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::quit(app, None)?)
        .build()?;

      // --- File menu (New Event… + Close Window) ---
      let new_event = MenuItemBuilder::new("New Event…")
        .id("new_event")
        .accelerator("CmdOrCtrl+N")
        .build(app)?;
      let file_menu = SubmenuBuilder::new(app, "File")
        .item(&new_event)
        .separator()
        .item(&PredefinedMenuItem::close_window(app, None)?)
        .build()?;

      // --- Edit/View menus (optional) ---
      let edit_menu = SubmenuBuilder::new(app, "Edit")
        .item(&PredefinedMenuItem::undo(app, None)?)
        .item(&PredefinedMenuItem::redo(app, None)?)
        .separator()
        .item(&PredefinedMenuItem::cut(app, None)?)
        .item(&PredefinedMenuItem::copy(app, None)?)
        .item(&PredefinedMenuItem::paste(app, None)?)
        .item(&PredefinedMenuItem::select_all(app, None)?)
        .build()?;
      let view_menu = SubmenuBuilder::new(app, "View")
        .item(&PredefinedMenuItem::fullscreen(app, None)?)
        .item(&PredefinedMenuItem::minimize(app, None)?)
        .build()?;

      // Attach menus (App menu must be first on macOS)
      let menu = MenuBuilder::new(app)
        .items(&[&app_menu, &file_menu, &edit_menu, &view_menu])
        .build()?;
      app.set_menu(menu)?;

      // --- Menu events ---
      app.on_menu_event(|app_handle, event| {
        match event.id().0.as_str() {
          "new_event" => {
            if let Some(w) = app_handle.get_webview_window("new-event") {
              let _ = w.set_focus();
            } else {
              let _ = WebviewWindowBuilder::new(
                app_handle,                                 // <-- &app_handle (not clone)
                "new-event",
                WebviewUrl::App("index.html".into()),
              )
              .title("New Event")
              .inner_size(640.0, 600.0)
              .resizable(true)
              .build();
            }
          }
          _ => {}
        }
      });

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
