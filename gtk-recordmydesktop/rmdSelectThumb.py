
import gtk
import gtk.gdk
#from rmdSelect import *
import gobject
import gc

class GtkThumbSelector(gtk.DrawingArea):
    def __init__(self,area_return,hidden,update_interval=2000):
        self.hidden=hidden
        self.area_return=area_return
        self.selecting=0
        gtk.DrawingArea.__init__(self)
        self.set_app_paintable(True)
        #self.fullscreen()
        self.connect("expose-event", self.expose_cb)
        self.connect("button-press-event", self.button_press_cb)
        self.connect("button-release-event", self.button_release_cb)
        self.connect("motion-notify-event", self.motion_notify_cb)
        #self.connect("delete-event", self.delete_cb)
        self.connect("realize", self.realize_cb)
        #root = gtk.gdk.get_default_root_window()
        self.wroot = gtk.gdk.get_default_root_window()
        (self.wwidth, self.wheight) = self.wroot.get_size()
        ###############################################################

        self.factor=1;
        twidth=self.wwidth
        while twidth>320 or self.factor<4:
          twidth/=2
          self.factor*=2
        self.root=gtk.gdk.Image(gtk.gdk.IMAGE_NORMAL,self.wroot.get_visual(),self.wwidth/self.factor,self.wheight/self.factor)
        #(width, height) = root.get_size()
        sroot = self.wroot.get_image(0, 0, self.wwidth, self.wheight)
        self.__subsample__(sroot,self.wwidth,self.wheight,self.root,self.factor)
        #self.root = root.get_image(0, 0, width, height)
        self.x1 = self.y1 = -1
        self.x2 = self.y2 = -1
        self.set_size_request(self.wwidth/self.factor,self.wheight/self.factor)
        self.timed_id=gobject.timeout_add(update_interval,self.update_image)
        
    def __subsample__(self,im1,w,h,im2,stride,x=0,y=0):
        for i in xrange(y,h,stride):
            for k in xrange(x,w,stride):
                im2.put_pixel(k/stride,i/stride,im1.get_pixel(k,i))    
    def button_release_cb(self, widget, event):
        if event.button == 1 and self.x1 >= 0 and widget==self:
            self.selecting=0
            self.x2 = event.x + 1
            self.y2 = event.y + 1
            # stop
            if self.x1 <0: self.x1=0
            if self.x2 <0: self.x2=0
            if self.y1 <0: self.y1=0
            if self.y2 <0: self.y2=0
            if self.x1 >self.wwidth/self.factor: self.x1=self.wwidth/self.factor
            if self.x2 >self.wwidth/self.factor: self.x2=self.wwidth/self.factor
            if self.y1 >self.wheight/self.factor: self.y1=self.wheight/self.factor
            if self.y2 >self.wheight/self.factor: self.y2=self.wheight/self.factor

                
            self.area_return[0]=min(int(self.x1),int(self.x2))*self.factor
            self.area_return[1]=min(int(self.y1),int(self.y2))*self.factor
            self.area_return[2]=max(int(self.x1),int(self.x2))*self.factor
            self.area_return[3]=max(int(self.y1),int(self.y2))*self.factor
            self.x1=self.y1=self.x2=self.y2=-1
            #print self.area_return
            self.update_image()
            
    def button_press_cb(self, widget, event):
        if widget==self:
            if event.button == 1:
                self.selecting=1
                self.update_image()
                self.x1 = event.x
                self.y1 = event.y
            else:
                self.x1 = self.y1=self.x2=self.y2=-1
                self.area_return[0]=self.area_return[1]=0
                self.area_return[2]=self.wwidth
                self.area_return[3]=self.wheight
                self.update_image()

    def realize_cb(self, widget):
        if widget == self:
            gdkwindow = self.window
            gdkwindow.set_events(gdkwindow.get_events() | 
                gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | 
                gtk.gdk.POINTER_MOTION_MASK);
            cursor = gtk.gdk.Cursor(gtk.gdk.CROSSHAIR)
            gdkwindow.set_cursor(cursor)
            gdkwindow.set_back_pixmap(None, False)
        
    def expose_cb(self, widget, event):
        if widget==self:
            dashes = [ 1.0, 2.0 ]
            cr = self.window.cairo_create()
            cr.rectangle(event.area.x, event.area.y, event.area.width, 
                event.area.height)
            cr.clip()
            self.window.draw_image(self.style.black_gc, self.root, event.area.x,
                event.area.y, event.area.x, event.area.y, event.area.width,
                event.area.height)
            cr.set_line_width(1.0)
            cr.set_source_rgba (1.0, 0.0, 0.0, 1.0)
            cr.set_dash (dashes, 0.0)
            cr.move_to (self.x1 - 0.5, 0.0)
            cr.line_to (self.x1 - 0.5, event.area.y + event.area.height) 
            cr.move_to (0.0, self.y1 - 0.5)
            cr.line_to (event.area.x + event.area.width, self.y1 - 0.5)
            cr.stroke ()
    
            if self.x1 >= 0:
                x = min(self.x1, self.x2)
                y = min(self.y1, self.y2)
                w = max(self.x1, self.x2) - x
                h = max(self.y1, self.y2) - y
                cr.set_dash ([], 0.0)
                cr.rectangle ( x, y, w, h)
                cr.fill()
                cr.set_source_rgba (0.0, 0.0, 0.5, 0.5)
                cr.rectangle (x + 0.5, y + 0.5, w - 1, h - 1)
                cr.stroke()
        
        return False

    def motion_notify_cb(self, widget, event):
        if widget ==self:
            self.queue_draw()
            
            if self.x1 >= 0 :
                rect = gtk.gdk.Rectangle()
                rect.x = min(self.x1, min(self.x2, event.x + 1))
                rect.width = max(self.x1, max(self.x2, event.x + 1)) - rect.x
                rect.y = min(self.y1, min(self.y2, event.y + 1))
                rect.height = max(self.y1, max(self.y2, event.y + 1)) - rect.y
                self.queue_draw_area(rect.x, rect.y, rect.width, rect.height)
    
            self.x2 = event.x + 1
            self.y2 = event.y + 1
            
        return True

    def update_image(self):
        #self.root.destroy()
        self.queue_draw()
        if self.hidden[0]==0 :
            gc.collect()
            sroot = self.wroot.get_image(0,0,self.wwidth,self.wheight)
            self.__subsample__(sroot,self.wwidth,self.wheight,self.root,self.factor)
            vals=[0,0, self.wwidth, self.wheight]
            if self.area_return[0]>=0:
                vals[0]=self.area_return[0]
            if self.area_return[1]>=0:
                vals[1]=self.area_return[1]
            if self.area_return[2]>=0:
                vals[2]=self.area_return[2]-self.area_return[0]
            if self.area_return[3]>=0:
                vals[3]=self.area_return[3]-self.area_return[1]
            if vals[0] >0 or vals[1] >0 or vals[2] <self.wwidth or vals[3] <self.wheight:
                if self.selecting==0:
                    self.__draw_lines__(self.root,vals,self.factor)
        return True
    def __draw_lines__(self,img,vals,factor):
        for i in xrange(vals[0]/factor,vals[0]/factor+vals[2]/factor):
            for k in range(2):
                img.put_pixel(i,vals[1]/factor+k,0xff0000)
                img.put_pixel(i,(vals[1]+vals[3]/2-k)/factor,0xff0000)
                img.put_pixel(i,(vals[1]+vals[3]-1-k)/factor,0xff0000)
        for i in xrange(vals[1]/factor,vals[1]/factor+vals[3]/factor):
            for k in range(2):
                img.put_pixel(vals[0]/factor+k,i,0xff0000)
                img.put_pixel((vals[0]+vals[2]/2-k)/factor,i,0xff0000)
                img.put_pixel((vals[0]+vals[2]-1-k)/factor,i,0xff0000)

#area_return=[-1,-1,-1,-1]

#w=GtkThumbSelector(area_return,0)
#w.show()
#gtk.main()
#print area_return



