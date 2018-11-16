# Maintainer: Juliette Monsel <j_4321@protonmail.com>
pkgname=workhourglass
pkgver=2.0.0
pkgrel=1
pkgdesc="Enhance your efficiency by timing your work and breaks"
arch=('any')
url="http://sourceforge.net/projects/workhourglass/"
license=('GPL3')
makedepends=('python-setuptools')
depends=('python-matplotlib' 'python-numpy' 'python-pillow' 'tk' 'desktop-file-utils')
source=("${pkgname}-${pkgver}.tar.gz")
sha512sums=('8d5e4e93d57cafbac726bc40f9b79004494b6097d12f04d7a2166144129a7e0a8fa1f4688433097723c437b46f7688d7baf1fba206b2df4d1d086e3ab13dc01c')

build() {
    cd "${pkgname}-${pkgver}"
    python setup.py build
}

package() {
    cd "${pkgname}-${pkgver}"
    python setup.py install --root="$pkgdir/" --prefix=/usr --optimize=1 --skip-build
    install -D -m755 "${pkgname}.desktop" "${pkgdir}/usr/share/applications/${pkgname}.desktop"
    install -D -m644 "WorkHourGlass/WorkHourGlass/images/icon48.png" "${pkgdir}/usr/share/pixmaps/${pkgname}.png"
}



