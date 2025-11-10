# Maintainer: Your Name <shardennn@gmail.com>
pkgname=taskmgr
pkgver=1.0
pkgrel=1
pkgdesc="Windows XP-style Task Manager for Linux"
arch=('any')
url="https://github.com/timurtom/taskmgr"
license=('GPL3')
depends=('python' 'python-psutil' 'python-gobject' 'gtk3')
source=("taskmgr.py"
        "taskmgr.desktop")
sha256sums=('SKIP'
            'SKIP')

package() {
  cd "$srcdir"
  
  install -Dm755 taskmgr.py "$pkgdir/usr/bin/taskmgr"
  install -Dm644 taskmgr.desktop "$pkgdir/usr/share/applications/taskmgr.desktop"
}
