import unittest
import savingiterator
import tempfile
import pprint
import subprocess
import os

class TestCParsing( unittest.TestCase ):
    def setUp( self ):
        self.maxDiff = None

    def _tempfile( self, contents ):
        t = tempfile.NamedTemporaryFile( suffix = ".h" )
        t.write( contents )
        t.flush()
        return t

    def _gccCPPIncludeDir( self ):
        if not hasattr( self, '_gccCPPIncludeDirCache' ):
            stdarg = subprocess.check_output( "locate stdarg.h | grep '/stdarg.h$' | grep '^/usr' | grep gcc", shell = True, stderr = subprocess.STDOUT ).strip()
            self._gccCPPIncludeDirCache = os.path.dirname( stdarg )
        return self._gccCPPIncludeDirCache

    def _simpleTest( self, contents, expected ):
        tested = savingiterator.SavingIterator()
        contentsFile = self._tempfile( contents )
        tested.process( contentsFile.name, includes = [ self._gccCPPIncludeDir() ] )
        if tested.saved != expected:
            pprint.pprint( tested.saved )
            pprint.pprint( expected )
        self.assertEquals( tested.saved, expected )

    def _testWithHeaders( self, headersContents, contents, expected ):
        tested = savingiterator.SavingIterator()
        headersContentsFile = self._tempfile( headersContents )
        contentsFile = self._tempfile( ( '#include "%s"\n' % headersContentsFile.name ) + contents )
        tested.process( contentsFile.name, includes = [ self._gccCPPIncludeDir() ] )
        if tested.saved != expected:
            pprint.pprint( tested.saved )
            pprint.pprint( expected )
        self.assertEquals( tested.saved, expected )

    def test_classDeclaration( self ):
        self._simpleTest( "class SuperDuper { int y; public: int x; private: int z; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [], fullTextNaked = "classSuperDuper{inty;public:intx;private:intz;}" ),
            dict( callbackName = "fieldDeclaration", name = "y", text = "int y" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "fieldDeclaration", name = "x", text = "int x" ),
            dict( callbackName = "accessSpec", access = "private" ),
            dict( callbackName = "fieldDeclaration", name = "z", text = "int z" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_namespace( self ):
        self._simpleTest( "namespace A { namespace B { int b; } namespace C { int c; } int a; }", [
            dict( callbackName = "enterNamespace", name = "A" ),
            dict( callbackName = "enterNamespace", name = "B" ),
            dict( callbackName = "variableDeclaration", name = "b", text = "int b" ),
            dict( callbackName = "leaveNamespace" ),
            dict( callbackName = "enterNamespace", name = "C" ),
            dict( callbackName = "variableDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveNamespace" ),
            dict( callbackName = "variableDeclaration", name = "a", text = "int a" ),
            dict( callbackName = "leaveNamespace" ),
        ] )

    def test_constructor( self ):
        self._simpleTest( "class SuperDuper { public: \nSuperDuper( int a, const char * b ) {}\n int c; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{public:SuperDuper(inta,constchar*b){}intc;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "constructorDefinition", templatePrefix = "", name = "SuperDuper", text = "SuperDuper",
                returnType = None, static = None, virtual = False, const = False, parameters = [
                dict( name = "a", text = "int a" ),
                dict( name = "b", text = "const char * b" ), ] ),
            dict( callbackName = "fieldDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveClass" ),
        ] )

#    def test_inheritance( self ):
#        self._simpleTest( "class Yuvu {}; class Mushu {}; class Udu {}; class SuperDuper : Yuvu, public Mushu, private Udu {};", [
#            dict( callbackName = "enterClass", name = "Yuvu", inheritance = [] ),
#            dict( callbackName = "leaveClass" ),
#            dict( callbackName = "enterClass", name = "Mushu", inheritance = [] ),
#            dict( callbackName = "leaveClass" ),
#            dict( callbackName = "enterClass", name = "Udu", inheritance = [] ),
#            dict( callbackName = "leaveClass" ),
#            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [ ( 'private', 'Yuvu' ), ( 'public', 'Mushu' ), ( 'private', 'Udu' ) ] ),
#            dict( callbackName = "leaveClass" ),
#        ] )

    def test_methodDefinition( self ):
        self._simpleTest( "class SuperDuper { public: \nint aFunction( int a ) { return 0; }\n int c; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{public:intaFunction(inta){return0;}intc;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "int", static = False, virtual = False, const = False, parameters = [
                dict( name = "a", text = "int a" ) ] ),
            dict( callbackName = "fieldDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_methodDeclaration( self ):
        self._simpleTest( "class SuperDuper { public: \nint aFunction( int a );\n int c; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{public:intaFunction(inta);intc;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "int", static = False, virtual = False, const = False, parameters = [
                dict( name = "a", text = "int a" ) ] ),
            dict( callbackName = "fieldDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_staticmethod( self ):
        self._simpleTest( "class SuperDuper { public: \nstatic int aFunction( int a );\n int c; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{public:staticintaFunction(inta);intc;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "int", static = True, virtual = False, const = False, parameters = [
                dict( name = "a", text = "int a" ) ] ),
            dict( callbackName = "fieldDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_constMethodDeclaration( self ):
        self._simpleTest( "class SuperDuper { public: \nint aFunction( int a ) const;\n int c; };", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{public:intaFunction(inta)const;intc;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "int", static = False, virtual = False, const = True, parameters = [
                dict( name = "a", text = "int a" ) ] ),
            dict( callbackName = "fieldDeclaration", name = "c", text = "int c" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_functionReturningStdString( self ):
        self._simpleTest( "#include <string>\nstd::string theString();", [
            dict( callbackName = "functionForwardDeclaration", templatePrefix = "", name = "theString", text = "std :: string theString",
                returnType = "std :: string", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ClassInheritance( self ):
        self._simpleTest( "class AInterface {};\nclass B : public AInterface {};", [
            dict( callbackName = "enterClass", name = "AInterface", inheritance = [],
                fullTextNaked = "classAInterface{}" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "enterClass", name = "B", inheritance = [ ( 'public', 'AInterface' ) ],
                fullTextNaked = "classB:publicAInterface{}" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_ClassPrivateInheritance( self ):
        self._simpleTest( "class AInterface {};\nclass B : private AInterface {};", [
            dict( callbackName = "enterClass", name = "AInterface", inheritance = [],
                fullTextNaked = "classAInterface{}" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "enterClass", name = "B", inheritance = [],
                fullTextNaked = "classB:privateAInterface{}" ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_LValueReference( self ):
        self._simpleTest( "class Result {};\nResult globalResult;\nResult & getResult() { return globalResult; }", [
            dict( callbackName = "enterClass", name = "Result", inheritance = [],
                fullTextNaked = "classResult{}" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "variableDeclaration", name = "globalResult", text = "Result globalResult" ),
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "getResult", text = "Result & getResult",
                returnType = "Result &", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ConstLValueReference( self ):
        self._simpleTest( "class Result {};\nResult globalResult;\nconst Result & getResult() { return globalResult; }", [
            dict( callbackName = "enterClass", name = "Result", inheritance = [],
                fullTextNaked = "classResult{}" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "variableDeclaration", name = "globalResult", text = "Result globalResult" ),
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "getResult", text = "const Result & getResult",
                returnType = "const Result &", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ReturningPointer( self ):
        self._simpleTest( "class Result {};\nResult globalResult;\nResult * getResult() { return & globalResult; }", [
            dict( callbackName = "enterClass", name = "Result", inheritance = [],
                fullTextNaked = "classResult{}" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "variableDeclaration", name = "globalResult", text = "Result globalResult" ),
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "getResult", text = "Result * getResult",
                returnType = "Result *", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ReturnTypeIsSharedPtr( self ):
        self._testWithHeaders( "template < typename T > class sharedptr {};", "sharedptr< int > func();", [
            dict( callbackName = "functionForwardDeclaration", templatePrefix = "", name = "func", text = "sharedptr < int > func",
                returnType = "sharedptr < int >", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ReturnTypeIsSharedPtr_FunctionDefinition( self ):
        self._testWithHeaders( "template < typename T > class sharedptr {};",
                                "sharedptr< int > func() { return sharedptr< int >(); }", [
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "func", text = "sharedptr < int > func",
                returnType = "sharedptr < int >", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ReturnTypeIsSharedPtr_Method( self ):
        self._testWithHeaders( "template < typename T > class sharedptr {};",
                "class A { public: sharedptr< int > func() { return sharedptr< int >(); } };", [
            dict( callbackName = "enterClass", name = "A", inheritance = [],
                fullTextNaked = "classA{public:sharedptr<int>func(){returnsharedptr<int>();}}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "func", text = "func",
                returnType = "sharedptr < int >", static = False, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_ReturnTypeIsSharedPtr_Method_Bugfix( self ):
        self._testWithHeaders( "template < typename T > class sharedptr {};",
                "class A { public: const sharedptr< int > func() const { return sharedptr< int >(); } };", [
            dict( callbackName = "enterClass", name = "A", inheritance = [],
                fullTextNaked = "classA{public:constsharedptr<int>func()const{returnsharedptr<int>();}}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "func", text = "func",
                returnType = "const sharedptr < int >", static = False, virtual = False, const = True, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_ReturnTypeIsSharedPtr_Method_BugfixOperatorSpace( self ):
        self._simpleTest( "class A { public: bool operator==( int other ) { return true; } };", [
            dict( callbackName = "enterClass", name = "A", inheritance = [],
                fullTextNaked = "classA{public:booloperator==(intother){returntrue;}}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "method", templatePrefix = "", name = "operator==", text = "operator==",
                returnType = "bool", static = False, virtual = False, const = False, parameters = [
                    dict( name = "other", text = "int other" ) ] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_Bugfix_ExplicilyRemoveCommentTokens( self ):
        self._simpleTest( "void /*hello*/ func() /* bye */ {}", [
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "func", text = "void func",
                returnType = "void", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_Bugfix_TrailingStaticKeywordInFunctionDefinition( self ):
        self._simpleTest( "void func() {} static void func2() {}", [
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "func", text = "void func",
                returnType = "void", static = True, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "func2", text = "void func2",
                returnType = "void", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_Bugfix_PureVirtualNotParsedCorrectly( self ):
        self._simpleTest( "class SuperDuper { virtual void aFunction() = 0;};", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{virtualvoidaFunction()=0;}" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "void", static = False, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_Bugfix_PureVirtualConstMethodDefinition( self ):
        self._simpleTest( "class SuperDuper { virtual void aFunction() const = 0;};", [
            dict( callbackName = "enterClass", name = "SuperDuper", inheritance = [],
                fullTextNaked = "classSuperDuper{virtualvoidaFunction()const=0;}" ),
            dict( callbackName = "method", templatePrefix = "", name = "aFunction", text = "aFunction",
                returnType = "void", static = False, virtual = False, const = True, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_ClassInheritanceOverrideConstMethod( self ):
        self._simpleTest( "class AInterface { virtual int f() const = 0; static int a;};\nclass B : public AInterface { int f() const override { return 0; }};", [
            dict( callbackName = "enterClass", name = "AInterface", inheritance = [],
                fullTextNaked = "classAInterface{virtualintf()const=0;staticinta;}" ),
            dict( callbackName = "method", templatePrefix = "", name = "f", text = "f",
                returnType = "int", static = False, virtual = False, const = True, parameters = [] ),
            dict( callbackName = "variableDeclaration", name = "a", text = "int a" ),
            dict( callbackName = "leaveClass" ),
            dict( callbackName = "enterClass", name = "B", inheritance = [ ( 'public', 'AInterface' ) ],
                fullTextNaked = "classB:publicAInterface{intf()constoverride{return0;}}" ),
            dict( callbackName = "method", templatePrefix = "", name = "f", text = "f",
                returnType = "int", static = False, virtual = False, const = True, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_NoExcept( self ):
        self._simpleTest( "int f() noexcept { return 0; } int g() noexcept;"
                "class A { public: A() noexcept; ~A() noexcept; void method() noexcept;};", [
            dict( callbackName = "functionDefinition", templatePrefix = "", name = "f", text = "int f",
                returnType = "int", static = True, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "functionForwardDeclaration", templatePrefix = "", name = "g", text = "int g",
                returnType = "int", static = True, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "enterClass", name = "A", inheritance = [],
                fullTextNaked = "classA{public:A()noexcept;~A()noexcept;voidmethod()noexcept;}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "constructorDefinition", templatePrefix = "", name = "A", text = "A",
                returnType = None, static = None, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "method", templatePrefix = "", name = "method", text = "method",
                returnType = "void", static = False, virtual = False, const = False, parameters = [] ),
            dict( callbackName = "leaveClass" ),
        ] )

    def test_ExternC( self ):
        self._simpleTest( 'extern "C" { int a; }\nextern "C" void f();', [
            dict( callbackName = "variableDeclaration", name = "a", text = "int a" ),
            dict( callbackName = "functionForwardDeclaration", templatePrefix = "", name = "f", text = "void f",
                returnType = "void", static = True, virtual = False, const = False, parameters = [] ),
        ] )

    def test_ExplicitConversionOperator( self ):
        self._simpleTest( 'class A { public: explicit operator int () { return 0; } };', [
            dict( callbackName = "enterClass", name = "A", inheritance = [],
                fullTextNaked = "classA{public:explicitoperatorint(){return0;}}" ),
            dict( callbackName = "accessSpec", access = "public" ),
            dict( callbackName = "conversionFunction", conversionType = "int", const = False ),
            dict( callbackName = "leaveClass" ),
        ] )

if __name__ == '__main__':
    unittest.main()