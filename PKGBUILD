# Maintainer: Your Name <your.email@example.com>
pkgname=KInstaller
pkgver=1.0
pkgrel=1
pkgdesc="An Arch Linux Package Assister"
arch=('any')
url="https://github.com/KornineQ/KInstaller"
license=('MIT')
depends=('python')
source=("https://github.com/KornineQ/KInstaller/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/KInstaller-$pkgver"
    python setup.py install --root="${pkgdir}" --optimize=1
}
