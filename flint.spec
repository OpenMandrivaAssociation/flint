%global with_snapshot 1

%if %{with_snapshot}
%global commit 4b383e23b39099f5ba09f7758023440e76277fc1
%global shortcommit %(c=%{commit}; echo ${c:0:7})
# date +%Y%m%d
%global date 20130801
%global snapshot .%{date}git%{shortcommit}
%else
%global snapshot %{nil}
%endif

Name:           flint
Version:        2.3
Release:        1%{snapshot}%{?dist}
Summary:        Fast Library for Number Theory
Group:          Applications/Engineering
License:        GPLv2+
URL:            http://www.flintlib.org/
%if %{with_snapshot}
Source0:        https://github.com/wbhart/flint2/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
%else
Source0:        http://www.flintlib.org/flint-%{version}.tar.gz
%endif

# Minor changes to configure and Makefile.in for proper use of ${_lib}
# and generation of a shared library with a soname
Patch0:         %{name}-rpmbuild.patch

# Workaround bug in the create_doc build program that triggers an error
# for lines with 79 width under special conditions
Patch1:         %{name}-docgen.patch

# Add extra check for environment variable if not finding data file
# to avoid make check failure if not already installed
Patch2:         %{name}-cpimport.patch

BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  ntl-devel
BuildRequires:  tex(latex)
BuildRequires:	texlive-collection-latexextra
BuildRequires:	texlive-collection-pictures

%global sover %(echo %{version} | cut -d. -f 1)


%description
FLINT is a C library for doing number theory, written by William Hart
and David Harvey.


%package        devel
Summary:        Development files for FLINT
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       gmp-devel%{?_isa}
Requires:       mpfr-devel%{?_isa}


%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        static
Summary:        Static libraries for FLINT
Group:          Development/Libraries
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}


%description    static
The %{name}-static package contains static libraries for
developing applications that use %{name}.


%prep
%if %{with_snapshot}
%setup -q -n flint2-%{commit}
%else
%setup -q
%endif

%patch0
%patch1
%patch2

# sanitize header files
ln -sf $PWD flint
sed -e 's@\(#[[:space:]]*include\)[[:space:]*]"\([^"]*\)"@\1 <flint/\2>@' \
    -i  `find . -name \*.c -o -name \*.h`
# revert some buggy ones
sed -e 's|#include <mpir.h>|#include <gmp.h>|' \
    -e 's|#include <flint/gmp.h>|#include <gmp.h>|' \
    -e 's|#include <flint/mpir.h>|#include <gmp.h>|' \
    -e 's|#include <flint/mpfr.h>|#include <mpfr.h>|' \
    -e 's|#include <flint/math.h>|#include <math.h>|' \
    -e 's|#include <flint/stdlib.h>|#include <stdlib.h>|' \
    -i  `find . -name \*.c -o -name \*.h`

%build
OS=Linux \
MACHINE=%{_arch} \
FLINT_LIB=libflint.so.%{sover} \
sh -x ./configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --with-gmp=%{_libdir} \
    --with-mpfr=%{_libdir} \
    --with-ntl=%{_libdir} \
    CFLAGS="%{optflags}"
make %{?_smp_mflags}

# Build the documentation
pushd doc/latex
    make manual
popd

%install
make DESTDIR=%{buildroot} install

pushd %{buildroot}%{_libdir}
  ln -s libflint.so.%{sover} libflint.so
popd


%check
make check FLINT_CPIMPORT=$PWD/qadic/CPimport.txt


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc AUTHORS NEWS README gpl-2.0.txt
%{_libdir}/libflint.so.%{sover}
%{_datadir}/flint


%files devel
%doc INSTALL doc/latex/%{name}-manual.pdf
%{_includedir}/flint
%{_libdir}/libflint.so


%files static
%{_libdir}/libflint.a


%changelog
* Mon Aug  5 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 2.3-1.20130801git4b383e2
- Update to pre 2.4 snapshot that supports gmp, required by sagemath 5.10

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon May  6 2013 Jerry James <loganjerry@gmail.com> - 1.6-7
- Rebuild for ntl 6.0.0

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 1 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 1.6-4
- Build with ntl support to have all symbols resolved.
- Force -fPIC in CFLAGS to avoid ntl link failures.

* Mon May  7 2012 Jerry James <loganjerry@gmail.com> - 1.6-3
- Update warning patch to fix bz 819333

* Mon Jan  9 2012 Jerry James <loganjerry@gmail.com> - 1.6-2
- Rebuild for GCC 4.7

* Thu Oct 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.6-1.2
- rebuild with new gmp without compat lib

* Mon Oct 10 2011 Peter Schiffer <pschiffe@redhat.com> - 1.6-1.1
- rebuild with new gmp

* Mon Jul 18 2011 Jerry James <loganjerry@gmail.com> - 1.6-1
- New upstream release
- Build against the system zn_poly instead of the included sources
- Make sure there is no PIC code in the static archive
- Link mpQS against the shared library instead of including the library
- Fix build errors and scary warnings with gcc 4.6
- Remove unnecessary spec file elements (BuildRoot, etc.)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jun 26 2010 Thomas Spura <tomspur@fedoraproject.org> - 1.5.2-1
- update to new version
- renew both patches

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 10 2009 Conrad Meyer <konrad@tylerc.org> - 1.2.0-1
- Bump to 1.2.0.

* Fri Mar 6 2009 Conrad Meyer <konrad@tylerc.org> - 1.0.21-1
- Bump to 1.0.21.
- Build static subpackage.

* Sat Dec 6 2008 Conrad Meyer <konrad@tylerc.org> - 1.0.18-1
- Bump to 1.0.18.
- Patches apply with --fuzz=0.

* Sat Nov 29 2008 Conrad Meyer <konrad@tylerc.org> - 1.0.17-1
- Initial package.
